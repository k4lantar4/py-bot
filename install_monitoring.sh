#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # بدون رنگ

# مسیر نصب
INSTALL_DIR="/opt/mrjbot"
MONITORING_DIR="$INSTALL_DIR/monitoring"

# بررسی دسترسی روت
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}این اسکریپت باید با دسترسی روت اجرا شود.${NC}"
    echo -e "${YELLOW}لطفاً با دستور sudo اجرا کنید.${NC}"
    exit 1
fi

# بررسی وجود دایرکتوری نصب
if [ ! -d "$INSTALL_DIR" ]; then
    echo -e "${RED}دایرکتوری نصب $INSTALL_DIR یافت نشد.${NC}"
    echo -e "${YELLOW}لطفاً ابتدا MRJBot را نصب کنید.${NC}"
    exit 1
fi

# ایجاد دایرکتوری مانیتورینگ
mkdir -p $MONITORING_DIR

# تابع نصب Prometheus
install_prometheus() {
    echo -e "${BLUE}در حال نصب Prometheus...${NC}"
    
    # ایجاد دایرکتوری‌های مورد نیاز
    mkdir -p $MONITORING_DIR/prometheus/data
    
    # ایجاد فایل پیکربندی Prometheus
    cat > $MONITORING_DIR/prometheus/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'mrjbot-backend'
    metrics_path: '/api/metrics'
    static_configs:
      - targets: ['backend:8000']
EOF
    
    echo -e "${GREEN}Prometheus با موفقیت پیکربندی شد.${NC}"
}

# تابع نصب Grafana
install_grafana() {
    echo -e "${BLUE}در حال نصب Grafana...${NC}"
    
    # ایجاد دایرکتوری‌های مورد نیاز
    mkdir -p $MONITORING_DIR/grafana/data
    mkdir -p $MONITORING_DIR/grafana/provisioning/datasources
    mkdir -p $MONITORING_DIR/grafana/provisioning/dashboards
    
    # ایجاد فایل پیکربندی منبع داده Prometheus
    cat > $MONITORING_DIR/grafana/provisioning/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
EOF
    
    # ایجاد فایل پیکربندی داشبورد
    cat > $MONITORING_DIR/grafana/provisioning/dashboards/dashboard.yml << EOF
apiVersion: 1

providers:
  - name: 'MRJBot Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF
    
    # ایجاد داشبورد پیش‌فرض
    cat > $MONITORING_DIR/grafana/provisioning/dashboards/mrjbot-dashboard.json << EOF
{
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": "-- Grafana --",
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "gnetId": null,
  "graphTooltip": 0,
  "id": 1,
  "links": [],
  "panels": [
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 2,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "node_cpu_seconds_total{mode=\\"user\\"}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "CPU Usage",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 0
      },
      "hiddenSeries": false,
      "id": 4,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "node_memory_MemTotal_bytes - node_memory_MemFree_bytes",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Memory Usage",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "bytes",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 8
      },
      "hiddenSeries": false,
      "id": 6,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "rate(container_cpu_usage_seconds_total{name=~\\"mrjbot.*\\"}[1m])",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Container CPU Usage",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    },
    {
      "aliasColors": {},
      "bars": false,
      "dashLength": 10,
      "dashes": false,
      "datasource": "Prometheus",
      "fill": 1,
      "fillGradient": 0,
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 12,
        "y": 8
      },
      "hiddenSeries": false,
      "id": 8,
      "legend": {
        "avg": false,
        "current": false,
        "max": false,
        "min": false,
        "show": true,
        "total": false,
        "values": false
      },
      "lines": true,
      "linewidth": 1,
      "nullPointMode": "null",
      "options": {
        "dataLinks": []
      },
      "percentage": false,
      "pointradius": 2,
      "points": false,
      "renderer": "flot",
      "seriesOverrides": [],
      "spaceLength": 10,
      "stack": false,
      "steppedLine": false,
      "targets": [
        {
          "expr": "container_memory_usage_bytes{name=~\\"mrjbot.*\\"}",
          "refId": "A"
        }
      ],
      "thresholds": [],
      "timeFrom": null,
      "timeRegions": [],
      "timeShift": null,
      "title": "Container Memory Usage",
      "tooltip": {
        "shared": true,
        "sort": 0,
        "value_type": "individual"
      },
      "type": "graph",
      "xaxis": {
        "buckets": null,
        "mode": "time",
        "name": null,
        "show": true,
        "values": []
      },
      "yaxes": [
        {
          "format": "bytes",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        },
        {
          "format": "short",
          "label": null,
          "logBase": 1,
          "max": null,
          "min": null,
          "show": true
        }
      ],
      "yaxis": {
        "align": false,
        "alignLevel": null
      }
    }
  ],
  "refresh": "5s",
  "schemaVersion": 22,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {
    "refresh_intervals": [
      "5s",
      "10s",
      "30s",
      "1m",
      "5m",
      "15m",
      "30m",
      "1h",
      "2h",
      "1d"
    ]
  },
  "timezone": "",
  "title": "MRJBot Dashboard",
  "uid": "mrjbot",
  "version": 1
}
EOF
    
    echo -e "${GREEN}Grafana با موفقیت پیکربندی شد.${NC}"
}

# تابع ایجاد فایل docker-compose برای مانیتورینگ
create_docker_compose() {
    echo -e "${BLUE}در حال ایجاد فایل docker-compose برای مانیتورینگ...${NC}"
    
    cat > $MONITORING_DIR/docker-compose.yml << EOF
version: '3'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: mrjbot_prometheus
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    restart: always
    networks:
      - mrjbot_network

  node-exporter:
    image: prom/node-exporter:latest
    container_name: mrjbot_node_exporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    restart: always
    networks:
      - mrjbot_network

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: mrjbot_cadvisor
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    restart: always
    networks:
      - mrjbot_network

  grafana:
    image: grafana/grafana:latest
    container_name: mrjbot_grafana
    volumes:
      - ./grafana/data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=mrjbot_admin
      - GF_USERS_ALLOW_SIGN_UP=false
    ports:
      - "3000:3000"
    restart: always
    networks:
      - mrjbot_network

networks:
  mrjbot_network:
    external: true
EOF
    
    echo -e "${GREEN}فایل docker-compose با موفقیت ایجاد شد.${NC}"
}

# تابع بروزرسانی فایل docker-compose اصلی
update_main_docker_compose() {
    echo -e "${BLUE}در حال بروزرسانی فایل docker-compose اصلی...${NC}"
    
    # بررسی وجود فایل docker-compose اصلی
    if [ ! -f "$INSTALL_DIR/docker-compose.yml" ]; then
        echo -e "${RED}فایل docker-compose.yml در مسیر $INSTALL_DIR یافت نشد.${NC}"
        return 1
    fi
    
    # افزودن متریک‌ها به سرویس backend
    sed -i '/backend:/,/^[^ ]/ s/environment:/environment:\n      - ENABLE_METRICS=true/' $INSTALL_DIR/docker-compose.yml
    
    echo -e "${GREEN}فایل docker-compose اصلی با موفقیت بروزرسانی شد.${NC}"
}

# تابع ایجاد اسکریپت راه‌اندازی مانیتورینگ
create_start_script() {
    echo -e "${BLUE}در حال ایجاد اسکریپت راه‌اندازی مانیتورینگ...${NC}"
    
    cat > $MONITORING_DIR/start_monitoring.sh << EOF
#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # بدون رنگ

# مسیر نصب
MONITORING_DIR="/opt/mrjbot/monitoring"

# بررسی وجود دایرکتوری مانیتورینگ
if [ ! -d "\$MONITORING_DIR" ]; then
    echo -e "\${RED}دایرکتوری مانیتورینگ \$MONITORING_DIR یافت نشد.${NC}"
    echo -e "\${YELLOW}لطفاً ابتدا سیستم مانیتورینگ را نصب کنید.${NC}"
    exit 1
fi

# راه‌اندازی سرویس‌های مانیتورینگ
echo -e "\${BLUE}در حال راه‌اندازی سرویس‌های مانیتورینگ...${NC}"
cd \$MONITORING_DIR && docker-compose up -d

# بررسی وضعیت سرویس‌ها
echo -e "\${BLUE}وضعیت سرویس‌های مانیتورینگ:${NC}"
cd \$MONITORING_DIR && docker-compose ps

echo -e "\${GREEN}سیستم مانیتورینگ با موفقیت راه‌اندازی شد.${NC}"
echo -e "\${BLUE}داشبورد Grafana در آدرس http://localhost:3000 در دسترس است.${NC}"
echo -e "\${BLUE}نام کاربری: admin${NC}"
echo -e "\${BLUE}رمز عبور: mrjbot_admin${NC}"

exit 0
EOF
    
    # اجرایی کردن اسکریپت
    chmod +x $MONITORING_DIR/start_monitoring.sh
    
    echo -e "${GREEN}اسکریپت راه‌اندازی مانیتورینگ با موفقیت ایجاد شد.${NC}"
}

# تابع ایجاد اسکریپت توقف مانیتورینگ
create_stop_script() {
    echo -e "${BLUE}در حال ایجاد اسکریپت توقف مانیتورینگ...${NC}"
    
    cat > $MONITORING_DIR/stop_monitoring.sh << EOF
#!/bin/bash

# رنگ‌ها برای خروجی
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # بدون رنگ

# مسیر نصب
MONITORING_DIR="/opt/mrjbot/monitoring"

# بررسی وجود دایرکتوری مانیتورینگ
if [ ! -d "\$MONITORING_DIR" ]; then
    echo -e "\${RED}دایرکتوری مانیتورینگ \$MONITORING_DIR یافت نشد.${NC}"
    echo -e "\${YELLOW}لطفاً ابتدا سیستم مانیتورینگ را نصب کنید.${NC}"
    exit 1
fi

# توقف سرویس‌های مانیتورینگ
echo -e "\${BLUE}در حال توقف سرویس‌های مانیتورینگ...${NC}"
cd \$MONITORING_DIR && docker-compose down

echo -e "\${GREEN}سرویس‌های مانیتورینگ با موفقیت متوقف شدند.${NC}"

exit 0
EOF
    
    # اجرایی کردن اسکریپت
    chmod +x $MONITORING_DIR/stop_monitoring.sh
    
    echo -e "${GREEN}اسکریپت توقف مانیتورینگ با موفقیت ایجاد شد.${NC}"
}

# تابع بروزرسانی فایل mrjbot
update_mrjbot_cli() {
    echo -e "${BLUE}در حال بروزرسانی فایل mrjbot...${NC}"
    
    # بررسی وجود فایل mrjbot
    if [ ! -f "/usr/local/bin/mrjbot" ]; then
        echo -e "${YELLOW}فایل mrjbot در مسیر /usr/local/bin یافت نشد.${NC}"
        echo -e "${YELLOW}دستورات مانیتورینگ به CLI اضافه نشد.${NC}"
        return 1
    fi
    
    # افزودن دستورات مانیتورینگ به فایل mrjbot
    sed -i '/پردازش دستورات/i \
# تابع شروع مانیتورینگ\
start_monitoring() {\
    echo -e "${BLUE}در حال شروع سرویس‌های مانیتورینگ...${NC}"\
    $INSTALL_DIR/monitoring/start_monitoring.sh\
}\
\
# تابع توقف مانیتورینگ\
stop_monitoring() {\
    echo -e "${BLUE}در حال توقف سرویس‌های مانیتورینگ...${NC}"\
    $INSTALL_DIR/monitoring/stop_monitoring.sh\
}' /usr/local/bin/mrjbot
    
    # افزودن دستورات به case
    sed -i '/help|--help|-h)/i \
    monitoring-start)\
        start_monitoring\
        ;;\
    monitoring-stop)\
        stop_monitoring\
        ;;' /usr/local/bin/mrjbot
    
    # افزودن دستورات به راهنما
    sed -i '/نمایش این راهنما/i \  ${GREEN}monitoring-start${NC}   شروع سرویس‌های مانیتورینگ\n  ${GREEN}monitoring-stop${NC}    توقف سرویس‌های مانیتورینگ' /usr/local/bin/mrjbot
    
    echo -e "${GREEN}فایل mrjbot با موفقیت بروزرسانی شد.${NC}"
}

# اجرای توابع نصب
echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}نصب سیستم مانیتورینگ MRJBot${NC}"
echo -e "${BLUE}===================================================${NC}"

install_prometheus
install_grafana
create_docker_compose
update_main_docker_compose
create_start_script
create_stop_script
update_mrjbot_cli

echo -e "${BLUE}===================================================${NC}"
echo -e "${GREEN}نصب سیستم مانیتورینگ با موفقیت انجام شد.${NC}"
echo -e "${BLUE}برای شروع سرویس‌های مانیتورینگ، دستور زیر را اجرا کنید:${NC}"
echo -e "${YELLOW}$MONITORING_DIR/start_monitoring.sh${NC}"
echo -e "${BLUE}یا${NC}"
echo -e "${YELLOW}mrjbot monitoring-start${NC}"
echo -e "${BLUE}===================================================${NC}"

exit 0 