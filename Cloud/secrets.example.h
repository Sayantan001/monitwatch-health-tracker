#include <pgmspace.h>

#define SECRET
#define THINGNAME "YOUR_THING_NAME"

const char WIFI_SSID[] = "YOUR_WIFI_NAME";
const char WIFI_PASSWORD[] = "YOUR_WIFI_PASSWORD";
const char AWS_IOT_ENDPOINT[] = "YOUR_ENDPOINT-ats.iot.REGION.amazonaws.com";

// Amazon Root CA 1 (download from AWS and paste here)
static const char AWS_CERT_CA[] PROGMEM = R"EOF(
-----BEGIN CERTIFICATE-----
PASTE_ROOT_CA_HERE
-----END CERTIFICATE-----
)EOF";

// Device certificate
static const char AWS_CERT_CRT[] PROGMEM = R"KEY(
-----BEGIN CERTIFICATE-----
PASTE_DEVICE_CERT_HERE
-----END CERTIFICATE-----
)KEY";

// Device private key
static const char AWS_CERT_PRIVATE[] PROGMEM = R"KEY(
-----BEGIN RSA PRIVATE KEY-----
PASTE_PRIVATE_KEY_HERE
-----END RSA PRIVATE KEY-----
)KEY";
