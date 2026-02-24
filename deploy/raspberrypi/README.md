# KIVAI Raspberry Pi Deployment (v1.0)

This guide deploys the **KIVAI Gateway** on a Raspberry Pi as a **systemd service**.

> Target: Raspberry Pi 3B+ (works on most Raspberry Pi models running Raspberry Pi OS).

---

## What you get

- KIVAI Gateway running as a background service
- Auto-start on boot
- Health + validate + execute endpoints exposed on your LAN

Default port: **8787**

---

## Assumptions

- You cloned this repo to: `/opt/kivai`
- You created a virtualenv at: `/opt/kivai/venv`
- You can SSH into the Pi as user `kivai`

If you haven’t done the install yet, use the quick path:

```bash
sudo mkdir -p /opt
sudo chown -R kivai:kivai /opt
cd /opt

git clone https://github.com/tech4life-beyond/kivai.git
cd /opt/kivai

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 1) Install the systemd unit

Copy:

- `/opt/kivai/deploy/raspberrypi/systemd/kivai-gateway.service`

to:

- `/etc/systemd/system/kivai-gateway.service`

Commands:

```bash
sudo cp /opt/kivai/deploy/raspberrypi/systemd/kivai-gateway.service /etc/systemd/system/kivai-gateway.service
sudo systemctl daemon-reload
```

---

## 2) Enable + start the service

```bash
sudo systemctl enable kivai-gateway
sudo systemctl start kivai-gateway
```

---

## 3) Verify status + view logs

Status:

```bash
sudo systemctl status kivai-gateway --no-pager
```

Logs:

```bash
journalctl -u kivai-gateway -n 200 --no-pager
```

---

## 4) Test from another machine on the same LAN

Replace `<PI_IP>` with your Raspberry Pi’s IP.

### Health

```bash
curl http://<PI_IP>:8787/health
```

Expected:

```json
{"status":"ok","service":"kivai-gateway","version":"0.1.0"}
```

### Validate (schema check)

```bash
curl -X POST http://<PI_IP>:8787/v1/validate \
  -H "Content-Type: application/json" \
  -d '{
    "intent_id":"demo-001",
    "intent":"device.ping",
    "target":{"device_id":"mock-001"},
    "meta":{"timestamp":"2026-02-20T00:00:00Z","language":"en","confidence":1.0}
  }'
```

Expected:

```json
{"ok":true,"message":"✅ Payload is valid!"}
```

### Execute (demo adapter)

This will only return `status: ok` if a demo/mock adapter is registered in the runtime.

```bash
curl -X POST http://<PI_IP>:8787/v1/execute \
  -H "Content-Type: application/json" \
  -d '{
    "intent":"power.on",
    "target":{"device_id":"samsung-tv-bedroom"},
    "meta":{"timestamp":"2026-02-20T00:00:00Z","language":"en","confidence":1.0}
  }'
```

---

## Updating KIVAI on the Pi (after GitHub merges)

```bash
cd /opt/kivai

git pull
source venv/bin/activate
pip install -r requirements.txt

sudo systemctl restart kivai-gateway
```

---

## Uninstall

```bash
sudo systemctl stop kivai-gateway
sudo systemctl disable kivai-gateway
sudo rm -f /etc/systemd/system/kivai-gateway.service
sudo systemctl daemon-reload
```

