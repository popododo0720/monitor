# 학교망 모니터링 시스템

## 구조

```
monitoring/
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml          # Prometheus 메인 설정
│   ├── rules/                  # Alert rule
│   └── targets/                # ★ 여기만 수정하면 장비 추가/삭제 됨
│       ├── servers.yml         # 서버 (Node Exporter)
│       ├── ping_network.yml    # 스위치/라우터 Ping
│       ├── snmp_switches.yml   # SNMP 대상 장비
│       └── http_targets.yml    # 웹서비스 HTTP 체크
├── grafana/
│   ├── dashboards/             # Grafana dashboard JSON 백업/프로비저닝
│   └── provisioning/           # datasource/dashboard 자동 등록 설정
├── alertmanager/
│   └── alertmanager.yml        # 알림 라우팅 설정
├── blackbox/
│   └── blackbox.yml            # Blackbox Exporter 설정
└── snmp/
    └── snmp.yml                # SNMP Exporter 설정
```

## 실행

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git python3
sudo systemctl enable --now docker

git clone https://github.com/popododo0720/monitor.git /root/monitor
cd /root/monitor
docker compose pull
docker compose up -d
docker compose ps
```

토폴로지 설정 저장 API는 systemd 서비스로 실행합니다.

```bash
sudo install -m 0644 systemd/topology-api.service /etc/systemd/system/topology-api.service
sudo systemctl daemon-reload
sudo systemctl enable --now topology-api.service
```

## 접속

- Grafana: https://서버IP:3000 (rhksfl / rhksfl)
- Prometheus: https://서버IP:9443
- Alertmanager: https://서버IP:9444
- Topology: http://서버IP:4480 또는 https://서버IP:4443

내부 로컬 포트:

- Prometheus: http://127.0.0.1:9090
- Grafana: http://127.0.0.1:3001
- Alertmanager: http://127.0.0.1:9093

## Alertmanager

Prometheus는 `prometheus/rules/*.yml`의 alert rule을 읽고 Alertmanager(`127.0.0.1:9093`)로 전송합니다.

현재 기본 receiver는 `blackhole`이라 실제 외부 알림은 보내지 않습니다. Discord/Slack/email/카카오워크 등 알림 채널을 정하면 `alertmanager/alertmanager.yml`의 receiver를 교체하면 됩니다.

기본 룰:

- `PrometheusTargetDown`: scrape target down
- `BlackboxProbeFailed`: ping/HTTP probe 실패
- `NodeFilesystemAlmostFull`: 디스크 여유 공간 10% 미만

## Grafana Provisioning

Grafana datasource와 대시보드는 repo 안의 파일로 관리합니다.

- datasource: `grafana/provisioning/datasources/prometheus.yml`
- dashboard provider: `grafana/provisioning/dashboards/dashboards.yml`
- dashboard JSON: `grafana/dashboards/*.json`

현재 토폴로지 대시보드는 provisioning 대상에서 제외했습니다.

## 장비 추가/삭제

`prometheus/targets/` 안의 yml 파일만 수정하면 **30초 내 자동 반영** (재시작 불필요).

```yaml
# 예: AP 추가
- targets:
    - 10.1.3.1    # 새 AP
    - 10.1.3.2    # 새 AP
  labels:
    group: ap
    building: main
    floor: "3"
```

## Node Exporter (타겟 서버에 설치)

```bash
# Ubuntu/Debian
sudo apt install prometheus-node-exporter

# 또는 바이너리 직접 설치
wget https://github.com/prometheus/node_exporter/releases/download/v1.8.2/node_exporter-1.8.2.linux-amd64.tar.gz
tar xvf node_exporter-*.tar.gz
sudo cp node_exporter-*/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter

# systemd 서비스 등록
sudo tee /etc/systemd/system/node_exporter.service <<EOF
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=node_exporter
ExecStart=/usr/local/bin/node_exporter

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
```

## SNMP 커뮤니티 스트링

`snmp/snmp.yml`의 `auths.public_v2.community` 값을 학교 장비의 실제 community string으로 변경.

## Grafana 추천 대시보드

Grafana에서 Import (+ 버튼) → Dashboard ID 입력:

- **1860** - Node Exporter Full (서버)
- **7587** - Blackbox Exporter (Ping/HTTP)
- **11169** - SNMP Interface (네트워크 트래픽)
