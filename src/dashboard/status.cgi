#!/bin/sh

echo "Content-Type: text/html; charset=UTF-8"
echo "Cache-Control: no-store"
echo ""

# ==========================================
# otterpi Status Dashboard v3.3
# ==========================================


# ==========================================
# Systemdaten
# ==========================================

HOST=$(hostname)

DATE=$(date '+%d.%m.%Y %H:%M:%S')


UPTIME=$(awk '
BEGIN {
    getline < "/proc/uptime"

    sec=int($1)

    d=int(sec/86400)
    sec%=86400

    h=int(sec/3600)
    sec%=3600

    m=int(sec/60)

    text=""

    if (d>0)
        text=d " Tag" (d==1?"":"e")

    if (h>0) {
        if (text!="")
            text=text ", "

        text=text h " Stunde" (h==1?"":"n")
    }

    if (m>0 || text=="") {

        if (text!="")
            text=text ", "

        text=text m " Minute" (m==1?"":"n")
    }

    print text
}')

BOOT=$(who -b | awk '{print $2,$3}' | xargs -I{} date -d "{}" '+%d. %B %Y, %H:%M Uhr')

OS=$(grep PRETTY_NAME /etc/os-release | cut -d'"' -f2)

KERNEL=$(uname -r)

MODEL=$(tr -d '\0' </proc/device-tree/model 2>/dev/null)

CORES=$(nproc)

RAM_GB=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)

HARDWARE="$MODEL (${CORES} Kerne, ${RAM_GB} GB RAM)"


# ==========================================
# Temperatur
# ==========================================

TEMP_RAW=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)

TEMP=$(awk "BEGIN {printf \"%.1f\", $TEMP_RAW/1000}")

TEMP_PERCENT=$(awk "BEGIN {printf \"%.0f\", $TEMP_RAW/1000}")


if [ "$TEMP_RAW" -lt 65000 ]; then
    TEMP_STATUS="ok"

elif [ "$TEMP_RAW" -lt 80000 ]; then
    TEMP_STATUS="warn"

else
    TEMP_STATUS="critical"

fi


# ==========================================
# CPU Load
# ==========================================

LOAD1=$(awk '{print $1}' /proc/loadavg)

LOAD5=$(awk '{print $2}' /proc/loadavg)

LOAD15=$(awk '{print $3}' /proc/loadavg)


LOAD="$LOAD1 / $LOAD5 / $LOAD15"


load_metric()
{
    awk -v load="$1" 'BEGIN {
        bar=load/4*100

        if (bar > 100)
            bar=100

        if (load < 2.0)
            status="ok"
        else if (load < 3.5)
            status="warn"
        else
            status="critical"

        printf "%.0f %s\n", bar, status
    }'
}


set -- $(load_metric "$LOAD1")
LOAD1_BAR=$1
LOAD1_STATUS=$2

set -- $(load_metric "$LOAD5")
LOAD5_BAR=$1
LOAD5_STATUS=$2

set -- $(load_metric "$LOAD15")
LOAD15_BAR=$1
LOAD15_STATUS=$2


# ==========================================
# CPU Frequenz
# ==========================================

CPU_FREQ=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq 2>/dev/null)

CPU_MAX=$(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq 2>/dev/null)


CPU_FREQ_MHZ=$((CPU_FREQ/1000))

CPU_MAX_MHZ=$((CPU_MAX/1000))

CPU_MAX_GHZ=$(awk "BEGIN {printf \"%.1f\", $CPU_MAX/1000000}")


# ==========================================
# Prozesse
# ==========================================

PROCESS_COUNT=$(ps -e --no-headers | wc -l)


# ==========================================
# RAM
# ==========================================

RAM_TOTAL=$(awk '/MemTotal/ {print $2}' /proc/meminfo)

RAM_AVAILABLE=$(awk '/MemAvailable/ {print $2}' /proc/meminfo)

RAM_USED=$((RAM_TOTAL-RAM_AVAILABLE))


RAM_TOTAL_MB=$((RAM_TOTAL/1024))

RAM_USED_MB=$((RAM_USED/1024))

RAM_AVAILABLE_MB=$((RAM_AVAILABLE/1024))


RAM_PERCENT=$((RAM_USED*100/RAM_TOTAL))


if [ "$RAM_PERCENT" -lt 70 ]; then

    RAM_STATUS="ok"

elif [ "$RAM_PERCENT" -le 85 ]; then

    RAM_STATUS="warn"

else

    RAM_STATUS="critical"

fi


# ==========================================
# Swap
# ==========================================

SWAP_TOTAL=$(free -m | awk '/Swap/ {print $2}')

SWAP_USED=$(free -m | awk '/Swap/ {print $3}')

SWAP_AVAILABLE=$((SWAP_TOTAL-SWAP_USED))


if [ "$SWAP_TOTAL" -gt 0 ]; then

    SWAP_PERCENT=$((SWAP_USED*100/SWAP_TOTAL))

else

    SWAP_PERCENT=0

fi


if [ "$SWAP_PERCENT" -lt 50 ]; then

    SWAP_STATUS="ok"

elif [ "$SWAP_PERCENT" -le 80 ]; then

    SWAP_STATUS="warn"

else

    SWAP_STATUS="critical"

fi


SWAP_DEVICE="nicht verfügbar"
SWAP_TYPE="unbekannt"
SWAP_STATE="inaktiv"


{
    read -r _

    if read -r SWAP_FOUND SWAP_KIND _; then

        SWAP_DEVICE=$SWAP_FOUND
        SWAP_TYPE=$SWAP_KIND
        SWAP_STATE="aktiv"

        case "$SWAP_DEVICE" in
        /dev/zram*)
            SWAP_TYPE="zram"
        ;;
        esac

    fi

} < /proc/swaps


# ==========================================
# Speicher / SD-Karte
# ==========================================

DISK_DATA=$(df -P -B1 / | awk '
NR==2 {
    printf "%.1f %.1f %.1f %d\n",
        $2/1073741824,
        $3/1073741824,
        $4/1073741824,
        $5
}')

set -- $DISK_DATA


DISK_SIZE="$1 GB"

DISK_USED="$2 GB"

DISK_FREE="$3 GB"

DISK_PERCENT=$4


if [ "$DISK_PERCENT" -lt 75 ]; then

    DISK_STATUS="ok"

elif [ "$DISK_PERCENT" -le 90 ]; then

    DISK_STATUS="warn"

else

    DISK_STATUS="critical"

fi


# Root-Partition, Dateisystem und Mountoptionen in einem Aufruf
ROOT_MOUNT_DATA=$(findmnt -rn -o SOURCE,FSTYPE,OPTIONS / 2>/dev/null)

set -- $ROOT_MOUNT_DATA

ROOT_SOURCE=$1
FILESYSTEM=$2
ROOT_OPTIONS=$3


# Gerätenamen auflösen, falls findmnt beispielsweise /dev/root liefert
ROOT_DEVICE=$(readlink -f "$ROOT_SOURCE" 2>/dev/null)

[ -n "$ROOT_DEVICE" ] || ROOT_DEVICE="$ROOT_SOURCE"
[ -n "$ROOT_DEVICE" ] || ROOT_DEVICE="nicht verfügbar"
[ -n "$FILESYSTEM" ] || FILESYSTEM="nicht verfügbar"


INODE_DATA=$(df -i / | awk 'NR==2 {print $2,$3,$5}')

set -- $INODE_DATA

INODE_TOTAL=$1
INODE_USED=$2
INODE_PERCENT=$(echo "$3" | tr -d '%')
INODE_FREE=$((INODE_TOTAL-INODE_USED))


format_number()
{
    echo "$1" | awk '
    {
        n=$1
        while (n >= 1000) {
            rest = n % 1000
            if (rest < 10)
                rest="00" rest
            else if (rest < 100)
                rest="0" rest

            result="." rest result
            n=int(n/1000)
        }

        print n result
    }'
}


INODE_TOTAL_FMT=$(format_number "$INODE_TOTAL")

INODE_USED_FMT=$(format_number "$INODE_USED")

INODE_FREE_FMT=$(format_number "$INODE_FREE")


if [ "$INODE_PERCENT" -lt 80 ]; then

    INODE_STATUS="ok"

elif [ "$INODE_PERCENT" -le 90 ]; then

    INODE_STATUS="warn"

else

    INODE_STATUS="critical"

fi


# Mountstatus des Root-Dateisystems
case ",$ROOT_OPTIONS," in

*,rw,*)
    ROOT_MOUNT_MODE="rw"
    ROOT_WRITE_STATUS="beschreibbar (rw)"
;;

*,ro,*)
    ROOT_MOUNT_MODE="ro"
    ROOT_WRITE_STATUS="nur lesbar (ro)"
;;

*)
    ROOT_MOUNT_MODE="unknown"
    ROOT_WRITE_STATUS="unbekannt"
;;

esac


# Physisches Elterngerät der Root-Partition ermitteln.
# Es wird nur intern für den passenden sysfs-Pfad benötigt.
PARENT_NAME=$(lsblk -nro PKNAME "$ROOT_DEVICE" 2>/dev/null)


if [ -n "$PARENT_NAME" ]; then

    SD_PATH="/sys/class/block/$PARENT_NAME/device"

else

    SD_PATH=""

fi


# Fallbacks
SD_MODEL="nicht verfügbar"
SD_TYPE="nicht verfügbar"
SD_DATE="nicht verfügbar"


# Die sysfs-Dateien werden mit dem Shell-Builtin read gelesen.
# Dadurch sind hierfür keine zusätzlichen cat-Prozesse nötig.
if [ -n "$SD_PATH" ] && [ -r "$SD_PATH/name" ]; then

    IFS= read -r SD_MODEL < "$SD_PATH/name"

    [ -n "$SD_MODEL" ] || SD_MODEL="nicht verfügbar"

fi


if [ -n "$SD_PATH" ] && [ -r "$SD_PATH/type" ]; then

    IFS= read -r SD_TYPE < "$SD_PATH/type"

    [ -n "$SD_TYPE" ] || SD_TYPE="nicht verfügbar"

fi


if [ -n "$SD_PATH" ] && [ -r "$SD_PATH/date" ]; then

    IFS= read -r SD_DATE < "$SD_PATH/date"

    [ -n "$SD_DATE" ] || SD_DATE="nicht verfügbar"

fi


# ==========================================
# Netzwerk
# ==========================================

IPV4=$(hostname -I | awk '{print $1}')

GATEWAY=$(ip route | awk '/default/ {print $3}')

IPV6=$(ip -6 addr show scope global 2>/dev/null |
grep inet6 |
grep -v fdb |
awk '{print $2}' |
cut -d/ -f1 |
head -1)


MAC=$(cat /sys/class/net/eth0/address 2>/dev/null)


interface_status()
{

IFACE="$1"


if [ ! -d "/sys/class/net/$IFACE" ]; then

    echo "nicht vorhanden"

    return

fi


if [ "$IFACE" = "wlan0" ]; then

    RFKILL=$(rfkill list wlan 2>/dev/null)

    case "$RFKILL" in

    *"Soft blocked: yes"*|*"Hard blocked: yes"*)

        echo "blockiert"
        return

    ;;

    esac

fi


LINK=$(ip link show "$IFACE" 2>/dev/null)


case "$LINK" in

*LOWER_UP*)

    if [ "$IFACE" = "eth0" ]; then

        CARRIER=$(cat /sys/class/net/$IFACE/carrier 2>/dev/null)

        if [ "$CARRIER" = "1" ]; then
            echo "verbunden"
        else
            echo "nicht verbunden"
        fi

    else

        STATE=$(cat /sys/class/net/$IFACE/operstate 2>/dev/null)

        if [ "$STATE" = "up" ]; then
            echo "verbunden"
        else
            echo "nicht verbunden"
        fi

    fi

;;

*UP*)

    echo "nicht verbunden"

;;

*)

    echo "deaktiviert"

;;

esac

}


ETH0_STATUS=$(interface_status eth0)

WLAN0_STATUS=$(interface_status wlan0)

network_lamp()
{

case "$1" in

verbunden)
    echo "lamp-ok"
;;

nicht\ verbunden)
    echo "lamp-warn"
;;

blockiert)
    echo "lamp-critical"
;;

deaktiviert)
    echo "lamp-off"
;;

*)
    echo "lamp-off"
;;

esac

}



# ==========================================
# Dienste
# ==========================================

service_state()
{

STATE=$(systemctl is-active "$1" 2>/dev/null)

case "$STATE" in

active)
    echo "active"
;;

activating)
    echo "starting"
;;

inactive)
    echo "stopped"
;;

failed)
    echo "failed"
;;

*)
    echo "unknown"
;;

esac

}


NGINX_STATUS=$(service_state nginx)

MESH_STATUS=$(service_state meshcentral)

PIHOLE_STATUS=$(service_state pihole-FTL)

FCGI_STATUS=$(service_state fcgiwrap)

SSH_STATUS=$(service_state ssh)

NETWORKMANAGER_STATUS=$(service_state NetworkManager)

TIMESYNC_STATUS=$(service_state systemd-timesyncd)


SERVICE_OK=0
SERVICE_TOTAL=0
SERVICE_WARNINGS=0
SERVICE_ERRORS=0
SERVICE_STATUS="ok"


for S in \
"$NGINX_STATUS" \
"$MESH_STATUS" \
"$PIHOLE_STATUS" \
"$FCGI_STATUS" \
"$SSH_STATUS" \
"$NETWORKMANAGER_STATUS" \
"$TIMESYNC_STATUS"

do

    SERVICE_TOTAL=$((SERVICE_TOTAL+1))

    case "$S" in
    active)
        SERVICE_OK=$((SERVICE_OK+1))
    ;;

    failed)
        SERVICE_ERRORS=$((SERVICE_ERRORS+1))
        SERVICE_STATUS="critical"
    ;;

    *)
        SERVICE_WARNINGS=$((SERVICE_WARNINGS+1))

        if [ "$SERVICE_STATUS" = "ok" ]; then
            SERVICE_STATUS="warn"
        fi
    ;;
    esac

done


# ==========================================
# Hardware Integrität
# ==========================================

THROTTLE_OUTPUT=$(vcgencmd get_throttled 2>/dev/null)
THROTTLE_HEX=${THROTTLE_OUTPUT#*=}
THROTTLE_AVAILABLE="no"


case "$THROTTLE_HEX" in
0x*)
    THROTTLE_DIGITS=${THROTTLE_HEX#0x}

    case "$THROTTLE_DIGITS" in
    ""|*[!0-9A-Fa-f]*)
        ;;
    *)
        THROTTLE_VALUE=$((THROTTLE_HEX + 0))
        THROTTLE_AVAILABLE="yes"
        ;;
    esac
;;
esac


throttle_status()
{
    if [ "$THROTTLE_AVAILABLE" != "yes" ]; then
        echo "unknown"

    elif [ $((THROTTLE_VALUE & $1)) -ne 0 ]; then
        echo "critical"

    elif [ $((THROTTLE_VALUE & $2)) -ne 0 ]; then
        echo "warn"

    else
        echo "ok"
    fi
}


hardware_text()
{
    case "$1" in
    ok)       echo "OK" ;;
    warn)     echo "seit Start aufgetreten" ;;
    critical) echo "aktuell aktiv" ;;
    *)        echo "unbekannt" ;;
    esac
}


worst_status()
{
    RESULT="ok"

    for STATE in "$@"; do
        case "$STATE" in
        critical)
            echo "critical"
            return
        ;;
        warn|unknown)
            RESULT="warn"
        ;;
        esac
    done

    echo "$RESULT"
}


UNDERVOLTAGE_STATUS=$(throttle_status 0x1 0x10000)
FREQ_LIMIT_STATUS=$(throttle_status 0x2 0x20000)
THROTTLE_STATUS=$(throttle_status 0x4 0x40000)
TEMP_LIMIT_STATUS=$(throttle_status 0x8 0x80000)


UNDERVOLTAGE=$(hardware_text "$UNDERVOLTAGE_STATUS")
FREQ_LIMIT=$(hardware_text "$FREQ_LIMIT_STATUS")
THROTTLE_TEXT=$(hardware_text "$THROTTLE_STATUS")
TEMP_LIMIT_TEXT=$(hardware_text "$TEMP_LIMIT_STATUS")


HARDWARE_STATUS=$(worst_status \
    "$UNDERVOLTAGE_STATUS" \
    "$FREQ_LIMIT_STATUS" \
    "$THROTTLE_STATUS" \
    "$TEMP_LIMIT_STATUS")


# ==========================================
# Gesamtstatus
# ==========================================

# Zusammengefasste Statuswerte
LOAD_STATUS=$(worst_status \
    "$LOAD1_STATUS" \
    "$LOAD5_STATUS" \
    "$LOAD15_STATUS")


case "$ROOT_MOUNT_MODE" in
rw) ROOT_STATUS="ok" ;;
ro) ROOT_STATUS="critical" ;;
*)  ROOT_STATUS="warn" ;;
esac


if [ "$SWAP_STATE" = "aktiv" ]; then
    SWAP_HEALTH="$SWAP_STATUS"
else
    SWAP_HEALTH="warn"
fi


# Einzelne Befunde zählen
WARNINGS=$SERVICE_WARNINGS
ERRORS=$SERVICE_ERRORS


add_finding()
{
    case "$1" in
    critical)
        ERRORS=$((ERRORS+1))
    ;;
    warn|unknown)
        WARNINGS=$((WARNINGS+1))
    ;;
    esac
}


# Eine fehlgeschlagene Hardwareabfrage ist ein Befund,
# nicht vier identische unbekannte Befunde.
if [ "$THROTTLE_AVAILABLE" = "yes" ]; then

    add_finding "$UNDERVOLTAGE_STATUS"
    add_finding "$FREQ_LIMIT_STATUS"
    add_finding "$THROTTLE_STATUS"
    add_finding "$TEMP_LIMIT_STATUS"

else

    add_finding "unknown"

fi


add_finding "$ROOT_STATUS"
add_finding "$TEMP_STATUS"
add_finding "$LOAD_STATUS"
add_finding "$RAM_STATUS"
add_finding "$SWAP_HEALTH"
add_finding "$DISK_STATUS"
add_finding "$INODE_STATUS"


if [ "$ERRORS" -gt 0 ]; then

    GLOBAL_STATUS="critical"
    GLOBAL_TEXT="Kritisch"

elif [ "$WARNINGS" -gt 0 ]; then

    GLOBAL_STATUS="warn"
    GLOBAL_TEXT="Warnung"

else

    GLOBAL_STATUS="ok"
    GLOBAL_TEXT="OK"

fi


# ==========================================
# Lampen
# ==========================================

lamp()
{

case "$1" in

ok)
    echo "lamp-ok"
;;

warn|unknown)
    echo "lamp-warn"
;;

critical)
    echo "lamp-critical"
;;

*)
    echo "lamp-off"
;;

esac

}


status_text()
{

case "$1" in

ok)
    echo "OK"
;;

warn)
    echo "Warnung"
;;

critical)
    echo "Fehler"
;;

unknown)
    echo "unbekannt"
;;

*)
    echo "unbekannt"
;;

esac

}


service_lamp()
{

case "$1" in

active)
    echo "lamp-ok"
;;

starting)
    echo "lamp-warn"
;;

failed)
    echo "lamp-critical"
;;

stopped|unknown)
    echo "lamp-off"
;;

esac

}


service_text()
{

case "$1" in

active)
    echo "aktiv"
;;

starting)
    echo "startet"
;;

stopped)
    echo "gestoppt"
;;

failed)
    echo "fehlgeschlagen"
;;

*)
    echo "unbekannt"
;;

esac

}


GLOBAL_LAMP=$(lamp "$GLOBAL_STATUS")

ETH0_LAMP=$(network_lamp "$ETH0_STATUS")

WLAN0_LAMP=$(network_lamp "$WLAN0_STATUS")


cat <<EOF
<!DOCTYPE html>
<html lang="de">

<head>

<meta charset="UTF-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>🦦 otterpi System Status</title>


<style>

* {
box-sizing:border-box;
}


body {

margin:0;

min-height:100vh;

font-family:
system-ui,
-apple-system,
BlinkMacSystemFont,
"Segoe UI",
sans-serif;


background:

linear-gradient(
rgba(10,20,30,.55),
rgba(10,20,30,.70)
),

url("/otter2.png");


background-size:cover;

background-position:center;

background-attachment:fixed;


color:white;

padding:30px;

}



.container {

width:min(1200px,95%);

margin:auto;


background:
rgba(20,35,50,.58);


backdrop-filter:blur(6px);


border-radius:25px;


padding:40px;


box-shadow:
0 20px 50px rgba(0,0,0,.4);

}



h1 {

text-align:center;

margin-top:0;

}



.subtitle {

text-align:center;

color:#d1d5db;

}



.grid {

display:grid;

grid-template-columns:
repeat(2,minmax(320px,1fr));

gap:20px;

}



.card {

background:
rgba(31,41,55,.78);


border:
1px solid rgba(255,255,255,.08);


border-radius:18px;


padding:20px;

}



.card h2 {

margin-top:0;

}



.integrity-grid {

display:grid;

grid-template-columns:
1fr 1fr;

gap:20px;

}


.integrity-line {

display:grid;

grid-template-columns:190px 1fr;

gap:12px;

align-items:center;

margin:0 0 16px 0;

}


.resource-list .integrity-line {

margin-bottom:8px;

}


.integrity-subline {

display:grid;

grid-template-columns:172px 1fr;

gap:12px;

align-items:center;

margin:0 0 5px 18px;

}


.network-line {

display:grid;

grid-template-columns:120px auto;

margin:0 0 0 0;

}


.service-line {

display:grid;

grid-template-columns:170px 130px auto;

margin:0 0 12px 0;

align-items:center;

}


.usage-line {

display:grid;

grid-template-columns:1fr auto;

gap:12px;

align-items:center;

margin:8px 0 16px 0;

}


.load-line {

display:grid;

grid-template-columns:65px 1fr auto;

gap:10px;

align-items:center;

margin:8px 0;

}


.small-load-line {

display:grid;

grid-template-columns:1fr auto;

gap:10px;

align-items:center;

margin:8px 0;

}


.inode-info {

font-size:.85rem;

color:#d1d5db;

opacity:.85;

line-height:1.6;

}


.load-line span:first-child {

white-space:nowrap;

}


.load-bar {

height:9px;

background:#374151;

border-radius:10px;

overflow:hidden;

position:relative;

}


.load-fill {

height:100%;

}


.service-head {

display:grid;

grid-template-columns:170px 130px auto;

margin-bottom:10px;

font-size:.85rem;

color:#d1d5db;

opacity:.8;

}


@media(max-width:700px){

.integrity-grid {

grid-template-columns:1fr;

}


}



.lamp {

display:inline-block;

width:18px;

height:18px;

border-radius:50%;

margin-right:8px;

vertical-align:middle;

}


.lamp-small {

display:inline-block;

width:10px;

height:10px;

border-radius:50%;

margin-right:6px;

vertical-align:middle;

}


.lamp-ok {

background:#22c55e;

}


.lamp-warn {

background:#eab308;

}


.lamp-critical {

background:#ef4444;

}


.lamp-off {

background:#6b7280;

}


.bar {

position:relative;

height:18px;

background:#374151;

border-radius:10px;

overflow:hidden;

}


.bar-marker {

position:absolute;

top:0;

bottom:0;

width:1px;

background:rgba(255,255,255,.35);

z-index:3;

}


.fill {

position:relative;

z-index:1;

height:100%;

}



.fill-ok {

background:#22c55e;

}


.fill-warn {

background:#eab308;

}


.fill-critical {

background:#ef4444;

}



.small {

font-size:.85rem;

color:#d1d5db;

opacity:.85;

}



.portal-button {

display:inline-block;

padding:10px 22px;

border-radius:20px;

background:
rgba(147,197,253,.15);


border:
1px solid rgba(147,197,253,.4);


color:#bfdbfe;

text-decoration:none;

}



.portal-button:hover {

background:
rgba(147,197,253,.3);

}



.footer {

text-align:center;

margin-top:30px;

}



@media(max-width:700px){

.grid {

grid-template-columns:1fr;

}


body {

padding:15px;

}


.container {

width:100%;

padding:20px;

border-radius:18px;

}


.card {

padding:16px;

}

}


</style>

</head>


<body>


<div class="container">


<h1>
🦦 otterpi System Status
</h1>


<div class="subtitle">

LAN only<br>

Letzte Prüfung: $DATE

</div>


<br>


<div class="card">


<h2>

🛡 Systemstatus -

<span class="lamp $GLOBAL_LAMP"></span>

$GLOBAL_TEXT

</h2>


<div class="integrity-grid">


<div>


<p><b>Integrität</b></p>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$HARDWARE_STATUS")"></span>
Hardware
</span>

<span>$(status_text "$HARDWARE_STATUS")</span>

</p>


<p class="integrity-subline">

<span>
<span class="lamp-small $(lamp "$UNDERVOLTAGE_STATUS")"></span>
Unterspannung
</span>

<span>$UNDERVOLTAGE</span>

</p>


<p class="integrity-subline">

<span>
<span class="lamp-small $(lamp "$FREQ_LIMIT_STATUS")"></span>
Frequenzbegrenzung
</span>

<span>$FREQ_LIMIT</span>

</p>


<p class="integrity-subline">

<span>
<span class="lamp-small $(lamp "$THROTTLE_STATUS")"></span>
Drosselung
</span>

<span>$THROTTLE_TEXT</span>

</p>


<p class="integrity-subline">

<span>
<span class="lamp-small $(lamp "$TEMP_LIMIT_STATUS")"></span>
Temperatur-Limit
</span>

<span>$TEMP_LIMIT_TEXT</span>

</p>


<br>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$ROOT_STATUS")"></span>
Root-Dateisystem
</span>

<span>$ROOT_WRITE_STATUS</span>

</p>


<br>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$SERVICE_STATUS")"></span>
Dienste
</span>

<span>$SERVICE_OK / $SERVICE_TOTAL aktiv</span>

</p>


</div>


<div class="resource-list">


<p><b>Ressourcen</b></p>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$TEMP_STATUS")"></span>
CPU-Temperatur
</span>

<span>$TEMP °C</span>

</p>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$LOAD_STATUS")"></span>
CPU-Last
</span>

<span>$LOAD</span>

</p>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$RAM_STATUS")"></span>
RAM
</span>

<span>$RAM_PERCENT %</span>

</p>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$SWAP_HEALTH")"></span>
zram-Swap
</span>

<span>$SWAP_PERCENT %</span>

</p>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$DISK_STATUS")"></span>
SD-Karte
</span>

<span>$DISK_PERCENT %</span>

</p>


<p class="integrity-line">

<span>
<span class="lamp-small $(lamp "$INODE_STATUS")"></span>
Inodes
</span>

<span>$INODE_PERCENT %</span>

</p>


<br>


<p class="integrity-line">

<span>Warnungen</span>

<span>$WARNINGS</span>

</p>


<p class="integrity-line">

<span>Fehler</span>

<span>$ERRORS</span>

</p>


</div>


</div>


</div>


<br>


<div class="grid">


<div class="card">

<h2>🖥 System</h2>

<p>
<b>Hostname:</b><br>
$HOST
</p>

<p>
<b>Hardware:</b><br>
$HARDWARE
</p>

<p>
<b>OS:</b><br>
$OS
</p>

<p>
<b>Kernel:</b><br>
$KERNEL
</p>

<p>
<b>Letzter Start:</b><br>
$BOOT
</p>

<p>
<b>Uptime:</b><br>
$UPTIME
</p>

</div>


<div class="card">

<h2>🌐 Netzwerk</h2>


<p>

<b>IPv4:</b><br>

$IPV4

</p>

<p>

<b>Gateway:</b><br>

$GATEWAY

</p>

<p>

<b>IPv6:</b><br>

$IPV6

</p>


<p>

<b>MAC (eth0):</b><br>

$MAC

</p>

<p style="margin-top:28px;">

<b>Interfaces:</b><br>

<div class="network-line">
<span>LAN (eth0):</span>
<span><span class="lamp-small $ETH0_LAMP"></span>$ETH0_STATUS</span>
</div>

<div class="network-line">
<span>WLAN (wlan0):</span>
<span><span class="lamp-small $WLAN0_LAMP"></span>$WLAN0_STATUS</span>
</div>

</p>


</div>


<div class="card">

<h2>🔧 Dienste</h2>

<div class="service-head">

<span>Dienst</span>
<span>Status</span>
<span>Zweck</span>

</div>


<div class="service-line">

<span>nginx</span>

<span>
<span class="lamp $(service_lamp "$NGINX_STATUS")"></span>
$(service_text "$NGINX_STATUS")
</span>

<span>Webserver</span>

</div>


<div class="service-line">

<span>MeshCentral</span>

<span>
<span class="lamp $(service_lamp "$MESH_STATUS")"></span>
$(service_text "$MESH_STATUS")
</span>

<span>Fernwartung</span>

</div>


<div class="service-line">

<span>pihole-FTL</span>

<span>
<span class="lamp $(service_lamp "$PIHOLE_STATUS")"></span>
$(service_text "$PIHOLE_STATUS")
</span>

<span>DNS / Filter</span>

</div>


<div class="service-line">

<span>fcgiwrap</span>

<span>
<span class="lamp $(service_lamp "$FCGI_STATUS")"></span>
$(service_text "$FCGI_STATUS")
</span>

<span>CGI-Ausführung</span>

</div>


<div class="service-line">

<span>ssh</span>

<span>
<span class="lamp $(service_lamp "$SSH_STATUS")"></span>
$(service_text "$SSH_STATUS")
</span>

<span>Administration</span>

</div>


<div class="service-line">

<span>NetworkManager</span>

<span>
<span class="lamp $(service_lamp "$NETWORKMANAGER_STATUS")"></span>
$(service_text "$NETWORKMANAGER_STATUS")
</span>

<span>Netzwerkverwaltung</span>

</div>


<div class="service-line">

<span>systemd-timesyncd</span>

<span>
<span class="lamp $(service_lamp "$TIMESYNC_STATUS")"></span>
$(service_text "$TIMESYNC_STATUS")
</span>

<span>Zeitsynchronisation</span>

</div>


</div>


<div class="card">

<h2>⚡ Leistung</h2>


<p>

<b>CPU-Temperatur:</b>

</p>


<div class="usage-line">

<div class="bar">

<div class="bar-marker" style="left:65%;"></div>

<div class="bar-marker" style="left:80%;"></div>

<div class="fill fill-$TEMP_STATUS"
style="width:${TEMP_PERCENT}%">

</div>

</div>

<span>$TEMP °C</span>

</div>


<p>
<b>CPU-Last:</b>
</p>


<div class="load-line">

<span>1 min Ø</span>

<div class="load-bar">

<div class="bar-marker" style="left:50%;"></div>
<div class="bar-marker" style="left:87.5%;"></div>

<div class="load-fill fill-$LOAD1_STATUS"
style="width:${LOAD1_BAR}%">
</div>

</div>

<span>$LOAD1</span>

</div>


<div class="load-line">

<span>5 min Ø</span>

<div class="load-bar">

<div class="bar-marker" style="left:50%;"></div>
<div class="bar-marker" style="left:87.5%;"></div>

<div class="load-fill fill-$LOAD5_STATUS"
style="width:${LOAD5_BAR}%">
</div>

</div>

<span>$LOAD5</span>

</div>


<div class="load-line">

<span>15 min Ø</span>

<div class="load-bar">

<div class="bar-marker" style="left:50%;"></div>
<div class="bar-marker" style="left:87.5%;"></div>

<div class="load-fill fill-$LOAD15_STATUS"
style="width:${LOAD15_BAR}%">
</div>

</div>

<span>$LOAD15</span>

</div>


<p>

<b>CPU-Frequenz:</b><br>

$CPU_FREQ_MHZ MHz aktuell / $CPU_MAX_GHZ GHz max.

</p>


<p>

<b>Prozesse:</b><br>

$PROCESS_COUNT gesamt

</p>


</div>


<div class="card">

<h2>🧠 RAM</h2>


<p>

<b>$RAM_GB GB RAM ($RAM_TOTAL_MB MB nutzbar)</b>

</p>


<div class="usage-line">

<div class="bar">

<div class="bar-marker" style="left:70%;"></div>

<div class="bar-marker" style="left:85%;"></div>

<div class="fill fill-$RAM_STATUS"
style="width:${RAM_PERCENT}%">

</div>

</div>

<span>$RAM_PERCENT&nbsp;%</span>

</div>


$RAM_USED_MB MB genutzt / $RAM_AVAILABLE_MB MB verfügbar

</p>


<p>

<b>zram-Swap ($SWAP_TOTAL MB gesamt)</b>

</p>


<div class="usage-line">

<div class="load-bar">

<div class="bar-marker" style="left:50%;"></div>

<div class="bar-marker" style="left:80%;"></div>


<div class="load-fill fill-$SWAP_STATUS"
style="width:${SWAP_PERCENT}%">

</div>

</div>


<span>$SWAP_PERCENT&nbsp;%</span>

</div>


<p>

$SWAP_USED MB genutzt / $SWAP_AVAILABLE MB verfügbar

</p>


<div class="inode-info">

Swap-Gerät: $SWAP_DEVICE ·
Typ: $SWAP_TYPE ·
Status: $SWAP_STATE

</div>


</div>


<div class="card">

<h2>💾 SD-Karte / Speicher</h2>


<div class="usage-line">

<b>Modell: $SD_MODEL · Typ: $SD_TYPE ($DISK_SIZE gesamt)</b>

<span class="small">Herstellung: $SD_DATE</span>

</div>


<div class="usage-line">

<div class="bar">

<div class="bar-marker" style="left:75%;"></div>

<div class="bar-marker" style="left:90%;"></div>

<div class="fill fill-$DISK_STATUS"
style="width:${DISK_PERCENT}%">

</div>

</div>

<span>$DISK_PERCENT&nbsp;%</span>

</div>

<p>

$DISK_USED genutzt / $DISK_FREE verfügbar

</p>


<p>

<b>Inodes ($INODE_TOTAL_FMT gesamt)</b>

</p>


<div class="usage-line">

<div class="load-bar">

<div class="bar-marker" style="left:80%;"></div>

<div class="bar-marker" style="left:90%;"></div>

<div class="load-fill fill-$INODE_STATUS"
style="width:${INODE_PERCENT}%">

</div>

</div>

<span>$INODE_PERCENT&nbsp;%</span>

</div>


<p>

$INODE_USED_FMT genutzt / $INODE_FREE_FMT verfügbar

</p>


<div class="inode-info">

Root-Partition: $ROOT_DEVICE ·
Dateisystem: $FILESYSTEM ·
Status: $ROOT_WRITE_STATUS

</div>


</div>


</div>



<div class="footer">


<a class="portal-button"

href="http://makki.route64.de">

← Zurück zum Service-Portal

</a>


<br><br>


<span class="small">

🦦 otterpi · Status Dashboard v3.3

</span>


</div>


</div>


</body>

</html>

EOF
