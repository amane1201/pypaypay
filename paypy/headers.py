from __future__ import annotations
from typing import Dict
import uuid


# Values sourced from the decompiled PayPay Android app
# (jp.ne.paypay.android.coresdk.network.client.paypay.PayPayHttpHeaderFactory).
# The Android build ships more fields (device sensors, lock status, etc.),
# but this minimal set is what the BFF actually requires.
CLIENT_TYPE = "PAYPAYAPP"
CLIENT_OS_TYPE = "ANDROID"
CONTENT_TYPE = "application/json; charset=utf-8"

# Reasonable default that matches the app UA layout: "PaypayApp/<ver> Android<os>"
DEFAULT_APP_VERSION = "5.49.0"
DEFAULT_OS_VERSION = "13"
DEFAULT_TIMEZONE = "Asia/Tokyo"
DEFAULT_LOCALE = "ja"
DEFAULT_DEVICE_NAME = "Pixel 7"
DEFAULT_DEVICE_BRAND = "google"
DEFAULT_DEVICE_MANUFACTURER = "Google"
DEFAULT_DEVICE_HARDWARE = "panther"


def new_uuid() -> str:
    return str(uuid.uuid4())


def build_headers(
    *,
    client_uuid: str,
    device_uuid: str,
    access_token: str | None = None,
    app_version: str = DEFAULT_APP_VERSION,
    os_version: str = DEFAULT_OS_VERSION,
    timezone: str = DEFAULT_TIMEZONE,
    locale: str = DEFAULT_LOCALE,
    device_name: str = DEFAULT_DEVICE_NAME,
    device_brand: str = DEFAULT_DEVICE_BRAND,
    device_manufacturer: str = DEFAULT_DEVICE_MANUFACTURER,
    device_hardware: str = DEFAULT_DEVICE_HARDWARE,
    sandbox: bool = False,
) -> Dict[str, str]:
    h: Dict[str, str] = {
        "Client-UUID": client_uuid,
        "Device-UUID": device_uuid,
        "Client-Type": CLIENT_TYPE,
        "Client-Version": app_version,
        "Client-OS-Version": f"{os_version}.0.0",
        "Client-OS-Release-Version": os_version,
        "Client-OS-Type": CLIENT_OS_TYPE,
        "Client-Mode": "SANDBOX" if sandbox else "NORMAL",
        "Content-Type": CONTENT_TYPE,
        "Timezone": timezone,
        "System-Locale": locale,
        "User-Agent": f"PaypayApp/{app_version} Android{os_version}",
        "Device-Name": device_name,
        "Device-Brand-Name": device_brand,
        "Device-Manufacturer-Name": device_manufacturer,
        "Device-Hardware-Name": device_hardware,
        "Network-Status": "WIFI",
        "Is-Emulator": "false",
    }
    if access_token:
        h["Authorization"] = f"Bearer {access_token}"
    return h
