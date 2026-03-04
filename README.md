# 학교망 모니터링 시스템

## 구조

```
monitoring/
├── docker-compose.yml
├── prometheus/
│   ├── prometheus.yml          # Prometheus 메인 설정
│   └── targets/                # ★ 여기만 수정하면 장비 추가/삭제 됨
│       ├── servers.yml         # 서버 (Node Exporter)
│       ├── ping_network.yml    # 스위치/라우터 Ping
│       ├── ping_ap.yml         # AP Ping
│       ├── snmp_switches.yml   # SNMP 대상 장비
│       └── http_targets.yml    # 웹서비스 HTTP 체크
├── blackbox/
│   └── blackbox.yml            # Blackbox Exporter 설정
└── snmp/
    └── snmp.yml                # SNMP Exporter 설정
```

## 실행

```bash
docker compose up -d
```

## 접속

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin / changeme)

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
