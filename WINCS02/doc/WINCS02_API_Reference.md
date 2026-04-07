# WINCS02 API Specification

---
## Introduction

This reference manual provides information on the functions and features of the WINCS02 application programming interface (API). The API provides the functionality of a wireless LAN access device with integrated TCP/IP and TLS stack. Once the initial configuration has been performed, the device may access a Wi-Fi network and send/receive data.

### Product Support

**This reference manual refers to the interface API:**

<table>
<tbody>
<tr>
<td>Name</td>
<td>Version</td>
<td>Revision</td>
</tr>
<tr>
<td>WINCS02</td>
<td>3.2.0</td>
<td>a1ac4a492</td>
</tr>
</tbody>
</table>

### Definitions

In this document, the following naming conventions are used:

- API or Interface: The software functions which are provided to utilize the functionality described in this manual and the responses they create.

- App or Application: The software not described by this manual which uses the API functionality.

### Driver Initialization

The driver is initialized by calling **WINC_DevInit**. This function will initialize the driver state and prepare internal structures. The application must provide this function with a block of memory to act as a receive buffer for SPI operations, ideally this should be 2KBytes in size.

**WINC_DevInit** will return a **WINC_DEVICE_HANDLE** type device handle which can be used in future operations with the driver API. If initialization fails it will return a device handle value of **WINC_DEVICE_INVALID_HANDLE**.

``` c
WINC_DEVICE_HANDLE wincDevHandle;
WINC_DEV_INIT devInitData;
uint8_t devRcvBuffer[2048];

devInitData.pReceiveBuffer    = devRcvBuffer;
devInitData.receiveBufferSize = sizeof(devRcvBuffer);

wincDevHandle = WINC_DevInit(&devInitData);
```

### Transport Initialization

The driver uses an SDIO over SPI protocol to communicate with the WINCS02 device, this transport layer must be initialized before it can be used by the driver.

Device initialization can take some time, therefore the transport initialization can be perform synchronously or asynchronously. In both cases the function **WINC_SDIODeviceInit** is called. This function accepts a pointer to a state variable to maintain progress state and a pointer to a **WINC_SDIO_SEND_RECEIVE_FP** type SPI function which can send/receive SPI data.

**WINC_SDIODeviceInit** returns a **WINC_SDIO_STATUS_TYPE** status value indicating the result of the current operation. Negative values are fatal errors, zero represents success while positive value are ongoing states.

#### Synchronous Transport Initialization

If the application wishes to block while initialization is performed it may call **WINC_SDIODeviceInit** without a state parameter. The function will perform all operations required until either initialization is complete or an error condition is encountered.

``` c
bool APP_WINC_SPISendReceive(void* pTransmitData, void* pReceiveData, size_t size);

WINC_SDIO_STATUS_TYPE wincSDIOStatus;

wincSDIOStatus = WINC_SDIODeviceInit(NULL, APP_WINC_SPISendReceive);
```

#### Asynchronous Transport Initialization

To perform asynchronous initialization the application must provide a state parameter to **WINC_SDIODeviceInit**, this parameter will be updated by each call to **WINC_SDIODeviceInit**.

The **WINC_SDIO_STATUS_TYPE** return value of **WINC_SDIODeviceInit** indicates the status of the initialization, a positive value will be used to indicate the operation is still ongoing and the function should be called again to progress further. It is advisable to introduce a wait between calls as positive return values indicate the next stage in the process could not be run immediately.

``` c
bool APP_WINC_SPISendReceive(void* pTransmitData, void* pReceiveData, size_t size);

WINC_SDIO_STATUS_TYPE wincSDIOStatus;
WINC_SDIO_STATE_TYPE wincSDIOState;

wincSDIOState = WINC_SDIO_STATE_UNKNOWN;

do
{
    wincSDIOStatus = WINC_SDIODeviceInit(&wincSDIOState, APP_WINC_SPISendReceive);

    delay_ms(100);
}
while (wincSDIOStatus > 0)
```

---
### Asynchronous Event Codes

In most cases any output from the API will be in response to the receipt of a function call from the application. There are cases, however, where an asynchronous event occurs that the application will need informing of (e.g. disconnection from the network). The API uses Asynchronous Event Codes (AEC) to convey such events; AECs use the same message conventions as regular responses using a different message type to distinguish them.

The application must be prepared to receive AECs at any time as it is possible for the API to send ACEs resulting from a previous function or condition while the application is calling a new API function.

AECs are delivered to the application via the message callback registered by **WINC_DevAECCallbackRegister**.

---
### Command Functions and Responses

One or more command functions are grouped into Command Requests messages which are dispatched via **WINC_DevTransmitCmdReq**. The application must provide buffer a block of memory into which the Command Request message is constructed, this memory must persist until the **WINC_DEV_CMDREQ_EVENT_STATUS_COMPLETE** event has been received via the command response callback.

``` c
static void wincCmdRspCallback
(
    uintptr_t context,
    WINC_DEVICE_HANDLE devHandle,
    WINC_CMD_REQ_HANDLE cmdReqHandle,
    WINC_DEV_CMDREQ_EVENT_TYPE event,
    uintptr_t eventArg
)
{
    if (WINC_DEV_CMDREQ_EVENT_STATUS_COMPLETE == event)
    {
        free(cmdReqHandle);
    }
}

WINC_CMD_REQ_HANDLE cmdReqHandle;
uint8_t *pCmdReqBuffer;

/* Allocate a command request buffer */
pCmdReqBuffer = malloc(1024);

/* Initialize a command request for three messages */
cmdReqHandle = WINC_CmdReqInit(pCmdReqBuffer, 1024, 3, 0, wincCmdRspCallback, 0);

/* Add three command to the request message */
WINC_CmdEXAMPLE(cmdReqHandle, ARG1, ARG2);
WINC_CmdEXAMPLE(cmdReqHandle, ARG3, ARG4);
WINC_CmdEXAMPLE(cmdReqHandle, ARG5, ARG6);

/* Queue request message to be sent to device */
WDRV_WINC_DevTransmitCmdReq(wincDevHandle, cmdReqHandle)
```

Command responses are received by the callback registered when the Command Request was initialized by calling **WDRV_WINC_CmdReqInit**. Responses are delivered using the event **WINC_DEV_CMDREQ_EVENT_RSP_RECEIVED**. The end of responses for a single command will be signalled by the event **WINC_DEV_CMDREQ_EVENT_CMD_STATUS** via the callback. Once the status event has been received there will be no further direct command responses.

---
### Command Responses & AECs

Command response and AEC event information is carried in a **WINC_DEV_EVENT_RSP_ELEMS** structure to either the command response callback as a **WINC_DEV_CMDREQ_EVENT_RSP_RECEIVED** event or the AEC callback.

``` c
typedef struct
{
    uint16_t                rspCmdId;
    uint16_t                rspId;
    uint8_t                 numElems;
    WINC_DEV_EVENT_SRC_CMD  srcCmd;
    WINC_DEV_PARAM_ELEM     elems[10];
} WINC_DEV_EVENT_RSP_ELEMS;
```

This structure contains the IDs of the response message, number of elements contained and the elements themselves.

Optional response data is encoded in TLV type structures which describe the data received.

``` c
typedef struct
{
    WINC_TYPE   type;
    uint16_t    length;
    uint8_t     *pData;
} WINC_DEV_PARAM_ELEM;
```

The data should be extracted from these structures by calling **WINC_CmdReadParamElem**. This function will decode the received element into the user supplied storage location.

In addition for command responses the original command message that caused the response is provided. AECs do not provide this information.

``` c
typedef struct
{
    uint8_t idx;
    uint8_t numParams;
    uint8_t *pParams;
} WINC_DEV_EVENT_SRC_CMD;
```

This structure indicates position index within the original command request message, the number of parameters and the location of the packed TLV data.

The original command data can be unpacked for examination using the command **WINC_DevUnpackElements**. This creates an initialized list of **WINC_DEV_PARAM_ELEM** structures.

``` c
void appCmdRspCallback
(
    uintptr_t context,
    WINC_DEVICE_HANDLE devHandle,
    WINC_CMD_REQ_HANDLE cmdReqHandle,
    WINC_DEV_CMDREQ_EVENT_TYPE event,
    uintptr_t eventArg
)
{
    if (WINC_DEV_CMDREQ_EVENT_RSP_RECEIVED == event)
    {
        const WINC_DEV_EVENT_RSP_ELEMS *const pRspElems;

        pElems = (const WINC_DEV_EVENT_RSP_ELEMS *const)eventArg;

        if (NULL != pElems)
        {
            if (WINC_CMD_ID_EXAMPLE == pElems->rspId)
            {
                WINC_DEV_PARAM_ELEM elems[10];
                uint32_t elemValue;

                WINC_DevUnpackElements(pElems->srcCmd.numParams, pElems->srcCmd.pParams, elems)

                WINC_CmdReadParamElem(&elems[2], WINC_TYPE_INTEGER, &elemValue, sizeof(elemValue));
            }
        }
    }
}
```

---
## Overview

### Parameter Types

The definition of each function specifies the data types used for any associated parameter elements.

#### WINC_TYPE_STATUS

Status elements are used to convey the ID of a status message. The element is a 16-bit word where the top byte represents the module category of the message while the lower byte represents the specific message ID.

See [Status Response Codes](#_status_response_codes)

#### WINC_TYPE_INTEGER, WINC_TYPE_INTEGER_UNSIGNED

Integer elements represent signed and unsigned integers up to 32-bits.

#### WINC_TYPE_INTEGER_FRAC

Fractional integer element represents a fractional number in the form 'X.Y'. The element is a 32-bits word with a 16-bit integer value 'X' in the high word and a 16-bit fractional value 'Y' in the low word.

#### WINC_TYPE_STRING, WINC_TYPE_BYTE_ARRAY

The string and byte array elements carry essentially the same information, a series of bytes. The string type is not null-terminated. The purpose of the two types is simply to indicate how the information contained should be handled.

#### WINC_TYPE_IPV4ADDR

The IPv4 element contains an IPv4 address value. It can be either 4 bytes or 8 bytes. A 4 byte element represents a single IPv4 address, an 8 byte element represents an IPv4 address and netmask.

#### WINC_TYPE_IPV6ADDR

The IPv6 elelment contains an IPv6 arress value. It can be either 16 bytes or 17 bytes. A 16 byte element represents a single IPv6 address. a 17 byte element represents an IPv6 address and scope.

#### WINC_TYPE_BOOL

The bool element contains a single value of either 1 or 0 to represent True or False.

#### WINC_TYPE_MACADDR

The MAC address element contains a 6 byte array representing a MAC address.

#### WINC_TYPE_UTC_TIME

The UTC time element contains a 32-bit value representing a UTC time count.

---
<a id="_configuration_functions"></a>
### Configuration Functions

Certain functions are used to configure or query parts of the system. These commands allow the caller to set new parameter values and get existing parameter values. The functions can query all parameter values, query a single parameter ID, or set a single parameter ID.

Each configuration parameter will consist of an ID and a value.

Functions can have preceding arguments which are specific to that particular function, but the ID and value arguments will be the last arguments.

``` c
uint32_t optId, WINC_TYPE typeOptVal, uintptr_t optVal, size_t lenOptVal
```

To query all parameter values, the ID field of the function must be set to a special IGNORE value. If the configuration function was **WINC_CmdEXAMPLE** then the ignore value name would be **WINC_CMDEXAMPLE_ID_IGNORE_VAL**, i.e. **WINC_CMD\<NAME\>\_ID_IGNORE_VAL**. Using this value for `optId` will cause all paramater values to be queried and their values returned via the response callback. The value of subsequence arguments should be set to their IGNORE values as will.

``` c
WINC_CmdEXAMPLE(... , WINC_CMDEXAMPLE_ID_IGNORE_VAL, WINC_TYPE_INVALID, 0, 0);
```

To query a single paramter value, the ID field of the function must be set to the ID required. The name of the ID will be of the form **WINC_CFG_PARAM_ID\_\<NAME\>\_\<PARAM_NAME\>**.

For example, querying the parameter named **PARAM_ONE** would look like:

``` c
WINC_CFG_PARAM_ID_EXAMPLE_PARAM_ONE, WINC_TYPE_INVALID, 0, 0
```

To set a single parameter value, the VALUE arguments also need to be set. If the parameter value being set is an integer type the value is loaded directly into `optVal` (`lenOptVal` is ignored for these types), if the value is an array type value the address of the array is loaded into `optVal`.

For example, setting an integer value would look like:

``` c
WINC_CFG_PARAM_ID_EXAMPLE_PARAM_TWO, WINC_TYPE_INTEGER, newValue, 0
```

For example, setting an array value would look like:

``` c
WINC_CFG_PARAM_ID_EXAMPLE_PARAM_THREE, WINC_TYPE_BYTE_ARRAY, &newValue, sizeof(newValue)
```

#### Single Value Parameters:

These parameters may have only one value and are accessed using the parameter ID.

#### Multiple Value Parameters:

These parameters may have more than one value.

When reading all values, the parameter ID can be used, however when accessing a single value within the set of all values the function will use a fractional integer form of the ID consisting of \<ID\>.\<INDEX\>

<a id="EXAMPLE_ReadAllParamVal"></a>
**Reading all parameter values**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"value1")
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"value2")
    API->>APP: Response:WINC_CMD_ID_CMD(5.2,"value3")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

<a id="EXAMPLE_ReadSingleVal"></a>
**To read a single value**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCMD(5.1)
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"value2")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

---
When writing a value, the behavior will depend on the implementation of the command, however often writing a value to the parameter \<ID\> will cause an additional value to be appended to the set of parameter values, writing to the fractional \<ID\>.\<INDEX\> will cause that parameter index to be updated.

<a id="EXAMPLE_SetAddVal"></a>
**To set an additional value**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"value1")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    APP->>API: WINC_CmdCMD(5,"newvalue")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"value1")
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"newvalue")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

<a id="EXAMPLE_ReplaceAddVal"></a>
**To replace an existing value**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"value1")
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"value2")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    APP->>API: WINC_CmdCMD(5.0,"newvalue")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"newvalue")
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"value2")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

---
In addition to the fractional integer form a command response may include a range indication primarily to indicate how many valid responses will follow. This optional response will only be present if the parameter implements it and the request was to read all values, it will not be present if a request for a single value was made using a fractional integer ID.

The format of the range indication uses the non-fractional ID of the parameter and a single integer value:

This example indicates that WINC_CmdEXAMPLE parameter ID 5 will return 2 values, 5.0 and 5.1:

<a id="EXAMPLE_ValIDRange"></a>
**Range of IDs**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5,2)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"value1")
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"value2")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

#### Query Response Elements:

Standard configuration parameter queries return a simple \<ID\>,\<VALUE\> pair. For single value parameters the \<ID\> will be an integer, for multiple value parameters the \<ID\> will be a fractional integer in the form \<ID\>.0, \<ID\>.1 etc for each value.

<a id="EXAMPLE_SimpleIDVal"></a>
**Simple ID/Value**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"simple1")
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"simple2")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

#### Complex Value Elements:

When queried some configuration parameters will return a more complex value in place of the \<VALUE\> element of the response. A complex value is more than two element values.

<a id="EXAMPLE_ComplexIDVal"></a>
**Complex ID/Value**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCMD(5)
    API->>APP: Response:WINC_CMD_ID_CMD(5.0,"complex11","complex12","complex12")
    API->>APP: Response:WINC_CMD_ID_CMD(5.1,"complex21","complex22","complex22")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

#### Default Configurations and Presets:

Configuration commands are initially loaded with default values, also known as **preset 0**. Many configuration commands also support reloading preset values.

The reserved \<ID\> value 0 is used to query and load configuration command presets. Querying this \<ID\> will return the current base preset used to load the configuration commands values. Setting this \<ID\>'s value will load a preset set of values.

> [!NOTE]
> Currently only **preset 0** is defined to be the default system values. Other presets may be defined in future.

> [!NOTE]
> The queried preset indicates the preset last used to load the values in the configuration command, subsequent changes may have occurred to individual values. Therefore it does not indicate that any particular value is currently set to that preset value, only that it initially was.

<a id="EXAMPLE_Preset0IDVal"></a>
**Using preset 0**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Query all values
    APP->>API: WINC_CmdCMD()
    Note left of API: <ID> 1 default values is 1234
    API->>APP: Response:WINC_CMD_ID_CMD(1,1234)
    API->>APP: Response:WINC_CMD_ID_CMD(2,"A String")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    Note right of APP: Set <ID> 1 to be 5678
    APP->>API: WINC_CmdCMD(1,5678)
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    Note right of APP: Query all values
    APP->>API: WINC_CmdCMD()
    Note left of API: <ID> 1 now changed to 5678
    API->>APP: Response:WINC_CMD_ID_CMD(1,5678)
    API->>APP: Response:WINC_CMD_ID_CMD(2,"A String")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    Note right of APP: Query current base preset
    APP->>API: WINC_CmdCMD(0)
    Note left of API: Current preset is 0, default values
    API->>APP: Response:WINC_CMD_ID_CMD(0,0)
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    Note right of APP: Load preset 0 in to command values
    APP->>API: WINC_CmdCMD(0,0)
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
    Note right of APP: Query all values
    APP->>API: WINC_CmdCMD()
    Note left of API: <ID> 1 returned to default value
    API->>APP: Response:WINC_CMD_ID_CMD(1,1234)
    API->>APP: Response:WINC_CMD_ID_CMD(2,"A String")
    API->>APP: Status:WINC_CMD_ID_CMD(OK)
```

---
<a id="_status_response_codes"></a>
## Status Response Codes

| Value | Name | Description |
|----|----|----|
| 0x0000 | WINC_STATUS_OK | OK |
| 0x0001 | WINC_STATUS_ERROR | General Error |
| 0x0002 | WINC_STATUS_INVALID_CMD | Invalid AT Command |
| 0x0003 | WINC_STATUS_UNKNOWN_CMD | Unknown AT Command |
| 0x0004 | WINC_STATUS_INVALID_PARAMETER | Invalid Parameter |
| 0x0005 | WINC_STATUS_INCORRECT_NUM_PARAMS | Incorrect Number of Parameters |
| 0x0006 | WINC_STATUS_STORE_UPDATE_BLOCKED | Configuration Update Blocked |
| 0x0007 | WINC_STATUS_STORE_ACCESS_FAILED | Configuration Access Failed |
| 0x0008 | WINC_STATUS_TIMEOUT | Command Timed Out |
| 0x0009 | WINC_STATUS_HOST_INTERFACE_FAILED | Host Interface Failed |
| 0x000a | WINC_STATUS_ACCESS_DENIED | Access Denied |
| 0x000b | WINC_STATUS_CONFIG_CONFLICT | Configuration Conflict |

CORE Status Codes (Module ID = 0)

 

| Value | Name | Description |
|----|----|----|
| 0x0100 | WINC_STATUS_WIFI_API_REQUEST_FAILED | Wi-Fi Request Failed |
| 0x0101 | WINC_STATUS_STA_NOT_CONNECTED | STA Not Connected |
| 0x0102 | WINC_STATUS_NETWORK_ERROR | Network Error |
| 0x0103 | WINC_STATUS_FILE_SYSTEM_ERROR | File System Error |

[SYSTEM](#AN_MOD_SYSTEM) Status Codes (Module ID = 1)

 

| Value | Name | Description |
|----|----|----|
| 0x0300 | WINC_STATUS_CFG_NOT_PRESENT | Configuration not present |

[CFG](#AN_MOD_CFG) Status Codes (Module ID = 3)

 

| Value | Name | Description |
|----|----|----|
| 0x0500 | WINC_STATUS_DNS_TYPE_NOT_SUPPORTED | DNS Type Not Supported |
| 0x0501 | WINC_STATUS_DNS_TIMEOUT | DNS Query Timeout |
| 0x0502 | WINC_STATUS_DNS_ERROR | DNS Error |
| 0x0503 | WINC_STATUS_DNS_RECORD_NOT_FOUND | DNS Record Not Found |
| 0x0504 | WINC_STATUS_DNS_NON_EXISTENT_DOMAIN | DNS Non-Existent Domain |
| 0x0505 | WINC_STATUS_DNS_AUTH_DATA_ERROR | DNS Data Authentication Error |
| 0x0506 | WINC_STATUS_DNS_TRUNCATED_RESPONSE | DNS Response Truncated |

[DNS](#AN_MOD_DNS) Status Codes (Module ID = 5)

 

| Value | Name | Description |
|----|----|----|
| 0x0700 | WINC_STATUS_TSFR_PROTOCOL_NOT_SUPPORTED | Unsupported File Transfer Protocol |
| 0x0701 | WINC_STATUS_FILE_EXISTS | File Exists |
| 0x0702 | WINC_STATUS_FILE_NOT_FOUND | File Not Found |
| 0x0703 | WINC_STATUS_INVALID_FILE_TYPE | Invalid File Type |
| 0x0704 | WINC_STATUS_FILE_CREATE_FAILED | File create failed |
| 0x0705 | WINC_STATUS_FILE_WRITE_FAILED | File write failed |

[FS](#AN_MOD_FS) Status Codes (Module ID = 7)

 

| Value | Name | Description |
|----|----|----|
| 0x0800 | WINC_STATUS_MQTT_ERROR | MQTT Error |

[MQTT](#AN_MOD_MQTT) Status Codes (Module ID = 8)

 

| Value | Name | Description |
|----|----|----|
| 0x0900 | WINC_STATUS_NETWORK_INTF_DOWN | Network interface down |

[NETIF](#AN_MOD_NETIF) Status Codes (Module ID = 9)

 

| Value | Name | Description |
|----|----|----|
| 0x0a00 | WINC_STATUS_ERASE_DONE | Erase Done |
| 0x0a01 | WINC_STATUS_WRITE_DONE | Write Done |
| 0x0a02 | WINC_STATUS_VERIFY_DONE | Verify Done |
| 0x0a03 | WINC_STATUS_ACTIVATE_DONE | Activate Done |
| 0x0a04 | WINC_STATUS_INVALIDATE_DONE | Invalidate Done |
| 0x0a05 | WINC_STATUS_OTA_ERROR | OTA Error |
| 0x0a06 | WINC_STATUS_OTA_NO_STA_CONN | No STA Connection |
| 0x0a07 | WINC_STATUS_OTA_PROTOCOL_ERROR | Protocol Error |
| 0x0a08 | WINC_STATUS_OTA_TLS_ERROR | TLS Error |
| 0x0a09 | WINC_STATUS_OTA_IMG_TOO_LARGE | Image Exceeds |
| 0x0a0a | WINC_STATUS_OTA_TIMEOUT | Timeout |
| 0x0a0b | WINC_STATUS_OTA_VERIFY_FAILED | Image Verify Failed |

[OTA](#AN_MOD_OTA) Status Codes (Module ID = 10)

 

| Value | Name | Description |
|----|----|----|
| 0x0b00 | WINC_STATUS_PING_FAILED | Ping Failed |

[PING](#AN_MOD_PING) Status Codes (Module ID = 11)

 

| Value | Name | Description |
|----|----|----|
| 0x0d00 | WINC_STATUS_SNTP_SERVER_TMO | NTP Server Timeout |
| 0x0d01 | WINC_STATUS_SNTP_PROTOCOL_ERROR | NTP Protocol Error |

[SNTP](#AN_MOD_SNTP) Status Codes (Module ID = 13)

 

| Value | Name | Description |
|----|----|----|
| 0x0e00 | WINC_STATUS_SOCKET_ID_NOT_FOUND | Socket ID Not Found |
| 0x0e01 | WINC_STATUS_LENGTH_MISMATCH | Length Mismatch |
| 0x0e02 | WINC_STATUS_NO_FREE_SOCKETS | No Free Sockets |
| 0x0e03 | WINC_STATUS_SOCKET_INVALID_PROTOCOL | Invalid Socket Protocol |
| 0x0e04 | WINC_STATUS_SOCKET_CLOSE_FAILED | Socket Close Failed |
| 0x0e05 | WINC_STATUS_SOCKET_BIND_FAILED | Socket Bind Failed |
| 0x0e06 | WINC_STATUS_SOCKET_TLS_FAILED | Socket TLS Failed |
| 0x0e07 | WINC_STATUS_SOCKET_CONNECT_FAILED | Socket Connect Failed |
| 0x0e08 | WINC_STATUS_SOCKET_SEND_FAILED | Socket Send Failed |
| 0x0e09 | WINC_STATUS_SOCKET_SET_OPT_FAILED | Socket Set Option Failed |
| 0x0e0a | WINC_STATUS_SOCKET_REMOTE_NOT_SET | Socket Destination Not Set |
| 0x0e0b | WINC_STATUS_MULTICAST_ERROR | Multicast Error |
| 0x0e0c | WINC_STATUS_SOCKET_NOT_READY | Socket Not Ready |
| 0x0e0d | WINC_STATUS_SOCKET_SEQUENCE_ERROR | Socket Sequence Error |

[SOCKET](#AN_MOD_SOCKET) Status Codes (Module ID = 14)

 

| Value | Name | Description |
|----|----|----|
| 0x1000 | WINC_STATUS_TIME_ERROR | Time Error |

[TIME](#AN_MOD_TIME) Status Codes (Module ID = 16)

 

| Value | Name | Description |
|----|----|----|
| 0x1100 | WINC_STATUS_TLS_CA_CERT_MISSING | CA Cert Missing |
| 0x1101 | WINC_STATUS_TLS_CA_CERT_VALIDATION | CA Cert Validation |
| 0x1102 | WINC_STATUS_TLS_CA_CERT_DATE_VALIDATION | CA Cert Date Validation |
| 0x1103 | WINC_STATUS_TLS_KEY_PAIR_INCOMPLETE | Key Pair Incomplete |
| 0x1104 | WINC_STATUS_TLS_PEER_DOMAIN_MISSING | Peer Domain Missing |

[TLS](#AN_MOD_TLS) Status Codes (Module ID = 17)

 

| Value | Name | Description |
|----|----|----|
| 0x1200 | WINC_STATUS_WAP_STOP_REFUSED | Soft AP Stop Not Permitted |
| 0x1201 | WINC_STATUS_WAP_STOP_FAILED | Soft AP Stop Failed |
| 0x1202 | WINC_STATUS_WAP_START_REFUSED | Soft AP Start Not Permitted |
| 0x1203 | WINC_STATUS_WAP_START_FAILED | Soft AP Start Failed |
| 0x1204 | WINC_STATUS_UNSUPPORTTED_SEC_TYPE | Unsupported Security Type |

[WAP](#AN_MOD_WAP) Status Codes (Module ID = 18)

 

| Value | Name | Description |
|----|----|----|
| 0x1400 | WINC_STATUS_STA_DISCONN_REFUSED | STA Disconnect Not Permitted |
| 0x1401 | WINC_STATUS_STA_DISCONN_FAILED | STA Disconnect Failed |
| 0x1402 | WINC_STATUS_STA_CONN_REFUSED | STA Connection Not Permitted |
| 0x1403 | WINC_STATUS_STA_CONN_FAILED | STA Connection Failed |

[WSTA](#AN_MOD_WSTA) Status Codes (Module ID = 20)

 

| Value | Name | Description |
|----|----|----|
| 0x1600 | WINC_STATUS_ASSOC_NOT_FOUND | Association Not Found |

[ASSOC](#AN_MOD_ASSOC) Status Codes (Module ID = 22)

 

| Value | Name | Description |
|----|----|----|
| 0x1d00 | WINC_STATUS_NVM_LOCKED | NVM Locked Until Reset |

[NVM](#AN_MOD_NVM) Status Codes (Module ID = 29)

 

| Value | Name | Description |
|----|----|----|
| 0x1e00 | <span id="AN_STATUS_DFU_ADDRESS_WARNING"></span> WINC_STATUS_DFU_ADDRESS_WARNING | No Bootable Image In Other Partition |

[DFU](#AN_MOD_DFU) Status Codes (Module ID = 30)

 

| Value | Name | Description |
|----|----|----|
| 0x1f00 | WINC_STATUS_PPS_WIFI_PS_NOT_ENABLED | Wi-Fi PS Not Enabled |
| 0x1f01 | WINC_STATUS_PPS_TIMEOUT | PPS Timeout |
| 0x1f02 | WINC_STATUS_PPS_PAUSE_EXPIRED | PPS Pause Expired |

[PPS](#AN_MOD_PPS) Status Codes (Module ID = 31)

 

| Value | Name | Description |
|----|----|----|
| 0x2100 | WINC_STATUS_ARB_NO_INCREASE | The Value Provided Would Not Increase The ARB |
| 0x2101 | WINC_STATUS_ARB_REJECTED | The Value Provided Would Invalidate The Current Image |

[ARB](#AN_MOD_ARB) Status Codes (Module ID = 33)

 

| Value | Name | Description |
|----|----|----|
| 0x2200 | WINC_STATUS_HTTP_DNS_FAILED | HTTP DNS failed |
| 0x2201 | WINC_STATUS_HTTP_TLS_FAILED | HTTP TLS failed |
| 0x2202 | WINC_STATUS_HTTP_CONNECT_FAILED | HTTP connect failed |
| 0x2203 | WINC_STATUS_HTTP_MEMORY | HTTP buffer allocation |
| 0x2204 | WINC_STATUS_HTTP_RESPONSE_HEADERS | HTTP response format |
| 0x2205 | WINC_STATUS_HTTP_RECV_FAILED | HTTP receive failed |
| 0x2206 | WINC_STATUS_HTTP_SEND_FAILED | HTTP send failed |
| 0x2207 | WINC_STATUS_HTTP_TIMEOUT | HTTP timeout |

[HTTP](#AN_MOD_HTTP) Status Codes (Module ID = 34)

 

---
<a id="AN_MOD_SYSTEM"></a>
## SYSTEM (Module ID = 1)

### AEC Reference:

#### WINC_AEC_ID_BOOT

##### Description

**System has booted.**

| AEC         | Description |
|-------------|-------------|
| No Elements |             |

AEC Syntax

---
## INTERNAL (Module ID = 2)

### Function Reference:

#### WINC_CmdGMI

##### Description

This function requests manufacturer identification.

**bool WINC_CmdGMI(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

| Response   | Description          |
|------------|----------------------|
| \<MAN_ID\> | Information Response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;MAN_ID&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Manufacturers ID/name<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdGMM

##### Description

This function requests model identification.

**bool WINC_CmdGMM(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

| Response     | Description          |
|--------------|----------------------|
| \<MODEL_ID\> | Information Response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;MODEL_ID&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Model information<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdGMR

##### Description

This function requests revision identification.

**bool WINC_CmdGMR(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

| Response         | Description          |
|------------------|----------------------|
| \<VERSION_INFO\> | Information Response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;VERSION_INFO&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Version information<br />
</p></td>
</tr>
</tbody>
</table>

---
---
<a id="AN_MOD_CFG"></a>
## CFG (Module ID = 3)

### Function Reference:

#### WINC_CmdCFG

##### Description

This function is used to read or set the system configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdCFG
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDCFG_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_CFG_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>DEVICE_NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>The device name<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>VERSION</p></td>
<td style="text-align: left;"><p>INTEGER_FRAC<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Software version number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>PATCH</p></td>
<td style="text-align: left;"><p>INTEGER<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Software patch number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SECURITY</p></td>
<td style="text-align: left;"><p>INTEGER<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Security value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>BUILD_HASH</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Build ID<br />
Maximum length of string is 5<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>BUILD_TIME</p></td>
<td style="text-align: left;"><p>UTC_TIME<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Build time<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>CMD_PORT</p></td>
<td style="text-align: left;"><p>INTEGER<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Command port<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UART1</p></td>
<td style="text-align: left;"><p>UART1.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>CMD_BAUD</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Command baud rate<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>CMD_TIMEOUT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Command baud rate change timeout (ms)<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_CFG_STORE_ID_ARCHIVE_FILTER"></span> 50</p></td>
<td style="text-align: left;"><p>ARCHIVE_FILTER</p></td>
<td style="text-align: left;"><p>STRING<br />
INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Archive filter<br />
Maximum length of string is 32<br />
This is a multiple value parameter<br />
with an ID range 50.0 to 50.7<br />
</p>
<p>The filter is a list of command IDs either in string form ("+WSTAC") or integer form (0x1400).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_CFG_STORE_ID_ARCHIVE_SLOTS"></span> 51</p></td>
<td style="text-align: left;"><p>ARCHIVE_SLOTS</p></td>
<td style="text-align: left;"><p>UTC_TIME<br />
</p></td>
<td style="text-align: left;"><p>Archive slots<br />
This is a multiple value parameter<br />
with an ID range 51.1 to 51.2<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>52</p></td>
<td style="text-align: left;"><p>AUTOEXEC_STATUS</p></td>
<td style="text-align: left;"><p>STATUS<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Auto-execute status<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>100</p></td>
<td style="text-align: left;"><p>DEBUG_PORT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Debug port<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OFF</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UART1</p></td>
<td style="text-align: left;"><p>UART1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>UART2</p></td>
<td style="text-align: left;"><p>UART2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>101</p></td>
<td style="text-align: left;"><p>DEBUG_BAUD</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Debug baud rate<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_CFG_CFGCP"></a>
#### WINC_CmdCFGCP

##### Description

This function is used to copy configurations to/from storage.

Configurations managed by [WINC_CmdCFGCP](#AN_FUNC_AT_CFG_CFGCP) are groups of configuration command parameters. The command allows these parameters to be saved to either flash files or archive slots in memory for later retrival.

[WINC_CmdCFGCP](#AN_FUNC_AT_CFG_CFGCP) supports:

- Saving active configurations to flash files

- Saving active configurations to in memory archive slots

- Restoring flash files to active configuration

- Restoring flash files to in memory archive slots

- Restoring in memory archive slots to active configurations

- Duplicating in memory archive slots

> [!NOTE]
> Only parameter tables of configuration commands which have been changed are stored to flash files or archive slots.

**Active Configuration**

The active configuration is considered to occupy slot 0 for the purposes of the source and destination of [WINC_CmdCFGCP](#AN_FUNC_AT_CFG_CFGCP).

**Archive Slots**

Archive slots are numbered 1+, they represent in memory holding locations for configuration sets. The parameters in these slots are not active and not maintained through reset.

Slots can be queried through [ARCHIVE_SLOTS](#AN_FUNC_CFG_STORE_ID_ARCHIVE_SLOTS), these parameters contain the timestamp of the configuration set when stored from an active configuration.

A slot can be emptied by writing a zero value to the appropriate index within [ARCHIVE_SLOTS](#AN_FUNC_CFG_STORE_ID_ARCHIVE_SLOTS).

**Archive Filters**

The [ARCHIVE_FILTER](#AN_FUNC_CFG_STORE_ID_ARCHIVE_FILTER) contains a list of command IDs which are filtered out when storing or loading a configuration set. This allows a partial configuration to be stored or restored.

**Archive Files**

Configurations are stored in 'Configuration Files' types which can be queried and deleted through [WINC_CmdFSOP](#AN_FUNC_AT_FS_FLFS_FSOP).

**Configuration Summary**

The response to [WINC_CmdCFGCP](#AN_FUNC_AT_CFG_CFGCP) is a summary list of command IDs with the number of command elements being stored or restored and the total size of the memory used for that command.

**Auto-Execute Configuration**

If a configuration is stored to an archive file called 'autoexec' it will be automatically loaded during device boot, before a command prompt is presented.

    bool WINC_CmdCFGCP
    (
        WINC_CMD_REQ_HANDLE handle
        WINC_TYPE typeCfgsrc
        uintptr_t cfgsrc
        size_t lenCfgsrc
        WINC_TYPE typeCfgdst
        uintptr_t cfgdst
        size_t lenCfgdst
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeCfgsrc</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of cfgsrc.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>cfgsrc</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Configuration source.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenCfgsrc</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of cfgsrc.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeCfgdst</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of cfgdst.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>cfgdst</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Configuration destination.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenCfgdst</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of cfgdst.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                              | Description |
|---------------------------------------|-------------|
| \<CMD_ID\>,\<NUM_ITEMS\>,\<ITEM_LEN\> | copy event  |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CMD_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration command ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;NUM_ITEMS&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of items<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ITEM_LEN&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length of items<br />
</p></td>
</tr>
</tbody>
</table>

---
---
### Examples:

<a id="EXAMPLE_dc6130cfe9a84137759d254f2f775e9c95a1a939"></a>
**Saving active configuration to storage**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdWSTAC(1,"SSID")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    APP->>API: WINC_CmdWSTAC(2,3)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    APP->>API: WINC_CmdWSTAC(3,"Password")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    APP->>API: WINC_CmdNETIFC(0,20,1)
    API->>APP: Status:WINC_CMD_ID_NETIFC(OK)
    APP->>API: WINC_CmdDNSC(1,"1.1.1.1")
    API->>APP: Status:WINC_CMD_ID_DNSC(OK)
    APP->>API: WINC_CmdDNSC(2,0)
    API->>APP: Status:WINC_CMD_ID_DNSC(OK)
    APP->>API: WINC_CmdCFGCP(0,"saved")
    API->>APP: Response:WINC_CMD_ID_CFGCP(0x0500,3,49)
    API->>APP: Response:WINC_CMD_ID_CFGCP(0x0900,11,182)
    API->>APP: Response:WINC_CMD_ID_CFGCP(0x1400,10,136)
    API->>APP: Status:WINC_CMD_ID_CFGCP(OK)
```

<a id="EXAMPLE_52043c5b1266965e87fee1d62cf0473db94a8a9f"></a>
**Restoring configuration from storage**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdCFGCP("saved",0)
    API->>APP: Response:WINC_CMD_ID_CFGCP(0x0500,3,49)
    API->>APP: Response:WINC_CMD_ID_CFGCP(0x0900,11,182)
    API->>APP: Response:WINC_CMD_ID_CFGCP(0x1400,10,136)
    API->>APP: Status:WINC_CMD_ID_CFGCP(OK)
```

---
## DHCP (Module ID = 4)

### Function Reference:

#### WINC_CmdDHCPSC

##### Description

This function is used to read or set the DHCP server configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdDHCPSC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optIdx
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optIdx</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Pool index.<br />
</p>
<p>optIdx will be ignored if its value is<br />
WINC_CMDDHCPSC_IDX_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDDHCPSC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_DHCP_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>DCE’s internal DHCP Server<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>POOL_START</p></td>
<td style="text-align: left;"><p>IPV4ADDR<br />
</p></td>
<td style="text-align: left;"><p>Start address of DHCP server pool<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>POOL_END</p></td>
<td style="text-align: left;"><p>IPV4ADDR<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>End address of DHCP server pool<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>POOL_LEASES</p></td>
<td style="text-align: left;"><p>INTEGER<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Number of leases<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>NETIF_IDX</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Network interface index<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>GATEWAY</p></td>
<td style="text-align: left;"><p>IPV4ADDR<br />
</p></td>
<td style="text-align: left;"><p>The address of the default gateway<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
</p></td>
</tr>
</tbody>
</table>

---
---
<a id="AN_MOD_DNS"></a>
## DNS (Module ID = 5)

### Introduction:

#### Server Address Configuration

There are three methods available to configure the DNS servers used by the DCE.

1.  Manually configured via [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_SVR](#AN_FUNC_DNSC_STORE_ID_DNS_SVR).

2.  Automatically configured via IPv4 DHCP option 6.

3.  Automatically configured via IPv6 Router Advertisement RNDSS.

Switching between manual and automatic configuration is performed by [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_AUTO](#AN_FUNC_DNSC_STORE_ID_DNS_AUTO).

#### Resource Queries

The supported query types are listed in [WINC_CmdDNSRESOLV](#AN_FUNC_AT_DNS_DNSRESOLV) parameter [type](#AN_FUNC_AT_DNS_DNSRESOLV_TYPE), other types may be specified as well. For unknown type the [WINC_AEC_ID_DNSRESOLV](#AN_AEC_AT_DNS_DNSRESOLV) response will simply include the undecoded RR data.

The DNS query ANY is indirectly supported, it has generally been deprecated as a DNS query type and some servers do not respond to it. If the ANY query is specified the DCE will generate two separate queries for A and AAAA records. When generating the queries for ANY, the DCE will use the configuration of [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_PROTO_PREF](#AN_FUNC_DNSC_STORE_ID_DNS_PROTO_PREF) to determine selection and order of A and AAAA queries.

> [!NOTE]
> [DNS_PROTO_PREF](#AN_FUNC_DNSC_STORE_ID_DNS_PROTO_PREF) specifies the order of queries made, it does not control the order of responses received.

#### Reverse Address Queries

IP address to name queries can be made using a **PTR** (12) query in the form:

- \<IPv4 Addr\>.in-addr.arpa

- \<IPv6 Addr\>.ip6.arpa

---
#### Connection Types

The DNS modules supports UDP, TCP, TLS and Multicast-UDP for performing DNS queries.

The default connection method is to use UDP to port 53 of the servers configured either manually or through DHCP/RA.

##### DNS over UDP

For queries to be sent via UDP [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_CONN_PREF](#AN_FUNC_DNSC_STORE_ID_DNS_CONN_PREF) must be set to 0 (UDP/TLS). All connections to the configured servers will now be via UDP.

The UDP port on the server used for queries will be set by [DNS_SRV_PORT](#AN_FUNC_DNSC_STORE_ID_DNS_SRV_PORT) which defaults to 53.

##### DNS over TCP

For queries to be sent via TCP [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_CONN_PREF](#AN_FUNC_DNSC_STORE_ID_DNS_CONN_PREF) must be set to 1 (TCP/TLS). All connections to the configured servers will now be via TCP.

The TCP port on the server used for queries will be set by [DNS_SRV_PORT](#AN_FUNC_DNSC_STORE_ID_DNS_SRV_PORT) which defaults to 53.

Option [DNS_CONN_IDLE_TIMEOUT](#AN_FUNC_DNSC_STORE_ID_DNS_CONN_IDLE_TIMEOUT) can be used to set an idle timeout, the DNC module will request the IDLE timeout from the DNS server and honour that time period.

##### DNS over TLS

For queries to be sent via TLS [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_CONN_PREF](#AN_FUNC_DNSC_STORE_ID_DNS_CONN_PREF) must be set to 1 (TCP/TLS). All connections to the configured servers will now be via TLS.

The TLS port on the server used for queries will be set by [DNS_SRV_SECURE_PORT](#AN_FUNC_DNSC_STORE_ID_DNS_SRV_SECURE_PORT) which defaults to 853.

Option [DNS_CONN_IDLE_TIMEOUT](#AN_FUNC_DNSC_STORE_ID_DNS_CONN_IDLE_TIMEOUT) can be used to set an idle timeout, the DNC module will request the IDLE timeout from the DNS server and honour that time period.

---
#### DNSSEC Support

Support for DNSSEC is configured by [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_DNSSEC_MODE](#AN_FUNC_DNSC_STORE_ID_DNS_DNSSEC_MODE) which offers three possible modes of operation:

1.  No support, the DO bit of EDNS0 extended flags is not set indicating that the DCE is unaware of DNSSEC operations.

2.  DNSSEC aware, this sets the DO bit of EDNS0 extended flags to indicate that DNSSEC RRs should be sent in response to queries. These RRs will be past the to DTE for further processing.

3.  DNSSEC authenticated answer only. In addition to the previous state the DNS module will not process any query responses which do not have either the AA bit set (indicating the DNS server is an authority for the domain) or the AD bit set (indicating the server has authenticated the response).

#### Cache Control

Query responses are held in a small answer cache to speed up further queries. Records are held in the cache based on the TTL value specified in the records. In addition the DTE can set a cache timeout via [WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_CACHE_TTL](#AN_FUNC_DNSC_STORE_ID_DNS_CACHE_TTL) which, if lower than a response TTL, will override it causing records to be expired from the cache sooner.

#### MDNS Support

In addition to unicast DNS queries the DNS module supports multicast queries for those records in the **.local** domain.

[WINC_CmdDNSC](#AN_FUNC_AT_DNS_DNSC) option [DNS_MC_SRV_PREF](#AN_FUNC_DNSC_STORE_ID_DNS_MC_SRV_PREF) configures if either or both IPv4 and IPv6 multicast queries should be made. If [DNS_MC_SRV_PREF](#AN_FUNC_DNSC_STORE_ID_DNS_MC_SRV_PREF) is non-zero and the query domain is **.local** a multicast DNS query will be made.

---
### Function Reference:

<a id="AN_FUNC_AT_DNS_DNSC"></a>
#### WINC_CmdDNSC

##### Description

This function is used to read or set the DNS configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdDNSC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDDNSC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_DNS_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_SVR"></span> 1</p></td>
<td style="text-align: left;"><p>DNS_SVR</p></td>
<td style="text-align: left;"><p>IPV4ADDR<br />
IPV6ADDR<br />
</p></td>
<td style="text-align: left;"><p>DNS server IP address<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
Format of IPv6 address is<br />
A1|…​|A16 = A1A2::A15A16<br />
This is a multiple value parameter<br />
with an ID range 1.0 to 1.3<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_AUTO"></span> 2</p></td>
<td style="text-align: left;"><p>DNS_AUTO</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>DNS server auto-assignment<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>MANUAL</p></td>
<td style="text-align: left;"><p>Manual - use DNS_SVR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>AUTO</p></td>
<td style="text-align: left;"><p>Auto - through DHCP etc..</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DNS_TIMEOUT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>DNS timeout in milliseconds<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_PROTO_PREF"></span> 4</p></td>
<td style="text-align: left;"><p>DNS_PROTO_PREF</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Result protocol preference<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A_AAAA</p></td>
<td style="text-align: left;"><p>A preferred over AAAA records.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>AAAA_A</p></td>
<td style="text-align: left;"><p>AAAA preferred over A records.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>A</p></td>
<td style="text-align: left;"><p>A only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>AAAA</p></td>
<td style="text-align: left;"><p>AAAA only.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_CACHE_TTL"></span> 6</p></td>
<td style="text-align: left;"><p>DNS_CACHE_TTL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>DNS cache maximum TTL<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>TLS_CONF</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_DNSSEC_MODE"></span> 8</p></td>
<td style="text-align: left;"><p>DNS_DNSSEC_MODE</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>DNSSEC mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OFF</p></td>
<td style="text-align: left;"><p>DNSSEC awareness off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CD</p></td>
<td style="text-align: left;"><p>DNSSEC aware, checking disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>AD</p></td>
<td style="text-align: left;"><p>DNSSEC authenticated answers only.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_SRV_PORT"></span> 10</p></td>
<td style="text-align: left;"><p>DNS_SRV_PORT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>DNS server UDP/TCP port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_SRV_SECURE_PORT"></span> 11</p></td>
<td style="text-align: left;"><p>DNS_SRV_SECURE_PORT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>DNS server TLS port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_CONN_PREF"></span> 12</p></td>
<td style="text-align: left;"><p>DNS_CONN_PREF</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Connection preference<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>UDP_TLS</p></td>
<td style="text-align: left;"><p>UDP or TLS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>TCP_TLS</p></td>
<td style="text-align: left;"><p>TCP or TLS.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_MC_SRV_PREF"></span> 13</p></td>
<td style="text-align: left;"><p>DNS_MC_SRV_PREF</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Multicast server preference<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OFF</p></td>
<td style="text-align: left;"><p>Not used.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>IPv4</p></td>
<td style="text-align: left;"><p>IPv4 servers only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>IPv6</p></td>
<td style="text-align: left;"><p>IPv6 servers only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>IPANY</p></td>
<td style="text-align: left;"><p>IPv4 &amp; IPv6 servers.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_DNSC_STORE_ID_DNS_CONN_IDLE_TIMEOUT"></span> 14</p></td>
<td style="text-align: left;"><p>DNS_CONN_IDLE_TIMEOUT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>DNS connection idle timeout (in milliseconds)<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_DNS_DNSRESOLV"></a>
#### WINC_CmdDNSRESOLV

##### Description

This function is used to resolve domain names via DNS.

    bool WINC_CmdDNSRESOLV
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t type
        const uint8_t* pQueryName
        size_t lenQueryName
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_AT_DNS_DNSRESOLV_TYPE"></span>type</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Type of record.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pQueryName</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Query name to resolve.<br />
</p>
<p>Maximum length of string is 256<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenQueryName</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pQueryName.<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_DNS_DNSRESOLV"></a>
#### WINC_AEC_ID_DNSRESOLV

##### Description

**Resolve results.**

| AEC | Description |
|----|----|
| \<TYPE\>,\<QUERY_NAME\>,\<ADDRESS\> | A & AAAA response |
| \<TYPE\>,\<QUERY_NAME\>,\<NSDNAME\> | NS response |
| \<TYPE\>,\<QUERY_NAME\>,\<CNAME\> | CNAME response |
| \<TYPE\>,\<QUERY_NAME\>,\<MNAME\>,\<SERIAL\>,\<REFRESH\>,\<RETRY\>,\<EXPIRE\>,\<MINIMUM\>,\<RNAME\> | SOA response |
| \<TYPE\>,\<QUERY_NAME\>,\<PTRDNAME\> | PTR response |
| \<TYPE\>,\<QUERY_NAME\>,\<EXCHANGE\>,\<PREFERENCE\> | MX response |
| \<TYPE\>,\<QUERY_NAME\>,\<TXT_DATA\> | TXT response |
| \<TYPE\>,\<QUERY_NAME\>,\<TARGET\>,\<PRIORITY\>,\<WEIGHT\>,\<PORT\> | SRV response |
| \<TYPE\>,\<QUERY_NAME\>,\<KEY_TAG\>,\<ALGORITHM\>,\<DIGEST_TYPE\>,\<DIGEST\> | DS response |
| \<TYPE\>,\<QUERY_NAME\>,\<SIGNER_NAME\>,\<TYPE\>,\<ALGORITHM\>,\<LABELS\>,\<ORIG_TTL\>,\<SIG_EXPIRE\>,\<SIG_INCEPT\>,\<KEY_TAG\>,\<SIGNATURE\> | RRSIG response |
| \<TYPE\>,\<QUERY_NAME\>,\<NEXT_DOMAIN\>,\<TYPE_BIT_MAPS\> | NSEC response |
| \<TYPE\>,\<QUERY_NAME\>,\<FLAGS\>,\<PROTOCOL\>,\<ALGORITHM\>,\<PUBLIC_KEY\> | DNSKEY response |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Type of record<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A</p></td>
<td style="text-align: left;"><p>A.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>NS</p></td>
<td style="text-align: left;"><p>NS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>CNAME</p></td>
<td style="text-align: left;"><p>CNAME.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>SOA</p></td>
<td style="text-align: left;"><p>SOA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>PTR</p></td>
<td style="text-align: left;"><p>PTR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>MX</p></td>
<td style="text-align: left;"><p>MX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>16</p></td>
<td style="text-align: left;"><p>TXT</p></td>
<td style="text-align: left;"><p>TXT.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>28</p></td>
<td style="text-align: left;"><p>AAAA</p></td>
<td style="text-align: left;"><p>AAAA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>SRV</p></td>
<td style="text-align: left;"><p>SRV.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>43</p></td>
<td style="text-align: left;"><p>DS</p></td>
<td style="text-align: left;"><p>DS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>46</p></td>
<td style="text-align: left;"><p>RRSIG</p></td>
<td style="text-align: left;"><p>RRSIG.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>47</p></td>
<td style="text-align: left;"><p>NSEC</p></td>
<td style="text-align: left;"><p>NSEC.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>48</p></td>
<td style="text-align: left;"><p>DNSKEY</p></td>
<td style="text-align: left;"><p>DNSKEY.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>255</p></td>
<td style="text-align: left;"><p>ANY</p></td>
<td style="text-align: left;"><p>Unspecified.</p></td>
</tr>
</tbody>
</table>
<p><br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QUERY_NAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Original query name requested<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>IP_ADDRESS<br />
</p></td>
<td style="text-align: left;"><p>IP address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;NSDNAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Name server domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CNAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Canonical alias domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MNAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Primary name server domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SERIAL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Serial number<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;REFRESH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Zone refresh interval<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RETRY&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Zone refresh retry interval<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;EXPIRE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Zone expiry interval<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MINIMUM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Minimum exported RR TTL<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RNAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Mailbox domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PTRDNAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Pointer domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;EXCHANGE&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Exchange domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PREFERENCE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Preference<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TXT_DATA&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Descriptive text<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TARGET&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Target domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PRIORITY&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Host priority<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;WEIGHT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Relative service weight<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Service port<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY_TAG&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Key tag<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALGORITHM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Algorithm<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DIGEST_TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Digest type<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DIGEST&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Digest<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGNER_NAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Signer’s name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LABELS&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of labels<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ORIG_TTL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Original TTL<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIG_EXPIRE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Signature ixpiration<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIG_INCEPT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Signature inception<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGNATURE&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Signature<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;NEXT_DOMAIN&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Next domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TYPE_BIT_MAPS&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Type bit maps<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FLAGS&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Flags<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Protocol<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DNSSEC</p></td>
<td style="text-align: left;"><p>DNSSEC.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PUBLIC_KEY&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Public key<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_DNSERR

##### Description

**Resolve failure.**

| AEC                                    | Description     |
|----------------------------------------|-----------------|
| \<ERROR_CODE\>,\<TYPE\>,\<QUERY_NAME\> | Resolve failure |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Type of record<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A</p></td>
<td style="text-align: left;"><p>A.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>NS</p></td>
<td style="text-align: left;"><p>NS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>CNAME</p></td>
<td style="text-align: left;"><p>CNAME.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>SOA</p></td>
<td style="text-align: left;"><p>SOA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>PTR</p></td>
<td style="text-align: left;"><p>PTR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>MX</p></td>
<td style="text-align: left;"><p>MX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>16</p></td>
<td style="text-align: left;"><p>TXT</p></td>
<td style="text-align: left;"><p>TXT.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>28</p></td>
<td style="text-align: left;"><p>AAAA</p></td>
<td style="text-align: left;"><p>AAAA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>SRV</p></td>
<td style="text-align: left;"><p>SRV.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>43</p></td>
<td style="text-align: left;"><p>DS</p></td>
<td style="text-align: left;"><p>DS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>46</p></td>
<td style="text-align: left;"><p>RRSIG</p></td>
<td style="text-align: left;"><p>RRSIG.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>47</p></td>
<td style="text-align: left;"><p>NSEC</p></td>
<td style="text-align: left;"><p>NSEC.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>48</p></td>
<td style="text-align: left;"><p>DNSKEY</p></td>
<td style="text-align: left;"><p>DNSKEY.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>255</p></td>
<td style="text-align: left;"><p>ANY</p></td>
<td style="text-align: left;"><p>Unspecified.</p></td>
</tr>
</tbody>
</table>
<p><br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QUERY_NAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Original query name requested<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_1a51414e8ba4741b94b30368131eea0cbb47bc44"></a>
**A record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(1,"www.example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"www.example.com","55.123.145.67")
```

<a id="EXAMPLE_16834ed81435ec93ee5ab05838d2049cfc926893"></a>
**NS record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(2,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(2,"example.com","ns1.example.com")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(2,"example.com","ns2.example.com")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"ns1.example.com","192.168.0.1")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(28,"ns1.example.com","1234:5678:ABCD::123")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"ns2.example.com","192.168.0.2")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(28,"ns2.example.com","1234:5678:ABCD::124")
```

<a id="EXAMPLE_cee6b3bece566292845ee70ea593b9ac8aba61e9"></a>
**CNAME record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(5,"www.example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(5,"www.example.com","ano.example.com")
```

<a id="EXAMPLE_0e97d9dea705e94b6d7a47e08f327b1dbda26c32"></a>
**SOA record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(6,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(6,"example.com","ns1.example.com",1728655446,10800,3600,604800,3600,"admin.example.com")
```

<a id="EXAMPLE_63f20427cb830943792a52dd0a405d79e485df24"></a>
**PTR record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(12,"67.145.123.55.in-addr.arpa")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(12,"67.145.123.55.in-addr.arpa","www.example.com")
```

<a id="EXAMPLE_cbb40c171c40e12c1958a6d28ccc5ce92c11459e"></a>
**MX record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(15,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(15,"example.com","mailx.example.com",10)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"mailx.example.com","192.168.0.101")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(28,"mailx.example.com","1234:5678:ABCD::5101")
```

<a id="EXAMPLE_5cf4dd868566a7d4fdc78b7c53ddcfa7a037d936"></a>
**TXT record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(16,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(16,"example.com","v=spf1 mx a include:_spf.example.com include:_spf.example.com ~all")
```

<a id="EXAMPLE_c4b68ffc231410a6beda9e466887b74c3303c800"></a>
**AAAA record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(28,"www.example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(28,"www.example.com","1234:5678:ABC:D000::EF12")
```

<a id="EXAMPLE_28e1b5f3b9c1a408085681aa145de2efbbd6e948"></a>
**SRV record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(33,"_imaps._tcp.example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(33,"_imaps._tcp.example.com","imap.example.com",5,0,993)
```

<a id="EXAMPLE_d2156535c655505f729023b004f3d04d06179bf0"></a>
**DS record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(43,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(43,"example.com",2371,13,2,[E44A0F027788...0BEA77D781])
```

<a id="EXAMPLE_ea72626e881fc800924086c49107f7286274d8d5"></a>
**NSEC record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(47,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(47,"example.com","\\000.example.com",[00096205800C...01C0])
```

<a id="EXAMPLE_28a3cea6a630e35c1ab57bdc97cffb510aa9b719"></a>
**DNSKEY record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(48,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(48,"example.com",257,3,13,[99DB2CC14CAB...4BE7778A19])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(48,"example.com",256,3,13,[A09311112CF9...806B65E148])
```

<a id="EXAMPLE_4bb82ae1e9ae5473ddf7c13902fcf71c771395d2"></a>
**ANY record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(255,"www.example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"www.example.com","55.123.145.67")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(28,"www.example.com","1234:5678:ABC:D000::EF12")
```

<a id="EXAMPLE_0f54ad37f94345566cd88df9220d1c69b75d32c3"></a>
**A record query With DNSSEC awareness**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSC(8,1)
    API->>APP: Status:WINC_CMD_ID_DNSC(OK)
    APP->>API: WINC_CmdDNSRESOLV(1,"www.example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"www.example.com","123.45.67.1")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"www.example.com","123.45.67.2")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(46,"www.example.com","example.com",1,13,3,300,1760198187,1760018187,34505,[D48611C4E419...48196DD1F7])
```

<a id="EXAMPLE_e84478c18562abdd4e2bbc34a253cfb7f08e4f8c"></a>
**NSEC3PARAM (unknown type) record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSC(8,1)
    API->>APP: Status:WINC_CMD_ID_DNSC(OK)
    APP->>API: WINC_CmdDNSRESOLV(51,"example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(51,"example.com",[010000180853...A4C2])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(46,"example.com","example.com",51,8,2,86400,1761202386,1759992786,43065,[57BE130BD9BC3E...9A00B300EC])
```

<a id="EXAMPLE_214c64db604a29b4ab723f35f946650640cabcd6"></a>
**NSEC3 (unknown type) response to invalid A record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSRESOLV(1,"0000.example.com")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(6,"example.com","ns.example.com",2780200301,1200,180,1209600,60,"techadmin.example.com")
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(46,"example.com","example.com",6,13,2,3600,1760329634,1760066834,56352,[EB66F399ECCAD5...FEE205A641])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(46,"11g4e2qvorlg6fqtd14inr597c52fedl.example.com","example.com",50,13,3,60,1760329634,1760066834,56352,[E90FDC2BDB03...E5F0A9E1])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(50,"11g4e2qvorlg6fqtd14inr597c52fedl.example.com",[010000000014...00000002])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(46,"g5nshuef875ssknoqrrcqg2cait0snsd.example.com","example.com",50,13,3,60,1760329634,1760066834,56352,[331653EACEF4...38765448])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(50,"g5nshuef875ssknoqrrcqg2cait0snsd.example.com",[010000000014...00000002])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(46,"q0fhrs556u4ps37jqnta5dhrufgu4ths.example.com","example.com",50,13,3,60,1760329634,1760066834,56352,[AB0CB2CBC0A2...DDBBAE12])
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(50,"q0fhrs556u4ps37jqnta5dhrufgu4ths.example.com",[010000000014...00000290])
    API->>APP: AEC:WINC_AEC_ID_DNSERR(5.4,"DNS Non-Existent Domain",1,"0000.example.com")
```

<a id="EXAMPLE_de863d68160befb7fb06d0eb444512ffff122839"></a>
**Multicast A record query**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSC(13,3)
    API->>APP: Status:WINC_CMD_ID_DNSC(OK)
    APP->>API: WINC_CmdDNSRESOLV(1,"example.local")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"example.local","123.45.6.101")
```

<a id="EXAMPLE_47cd0626aaaf78a7d83763f709beb232b7a5a058"></a>
**MDNS-SD of local SSH services**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdDNSC(13,3)
    API->>APP: Status:WINC_CMD_ID_DNSC(OK)
    Note right of APP: PTR lookup for _ssh._tcp
    APP->>API: WINC_CmdDNSRESOLV(12,"_ssh._tcp.local")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(12,"_ssh._tcp.local","example._ssh._tcp.local")
    Note right of APP: SRV lookup for example.local SSH service
    APP->>API: WINC_CmdDNSRESOLV(33,"example._ssh._tcp.local")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(33,"example._ssh._tcp.local","example.local",0,0,22)
    Note right of APP: TXT lookup for example.local SSH service
    APP->>API: WINC_CmdDNSRESOLV(16,"example._ssh._tcp.local")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(16,"example._ssh._tcp.local",[])
    API->>APP: Status:WINC_CMD_ID_None(OK)
    Note right of APP: A record lookup for example.local
    APP->>API: WINC_CmdDNSRESOLV(1,"example.local")
    API->>APP: Status:WINC_CMD_ID_DNSRESOLV(OK)
    API->>APP: AEC:WINC_AEC_ID_DNSRESOLV(1,"example.local","123.45.6.101")
```

---
<a id="AN_MOD_FS"></a>
## FS (Module ID = 7)

### Function Reference:

<a id="AN_FUNC_AT_FS_FLFS_FSOP"></a>
#### WINC_CmdFSOP

##### Description

This function performs a filesystem operation.

These operations use the WINC_CMD_ID_FS command request, therefore all status and response messages received will be using the WINC_CMD_ID_FS command ID. Messages are further identified by their \<OP\> response value indicating the type of operation involved.

The filesystem operation command is split into several sub-commands:

- List

- Delete

- Info

###### List Sub-Command:

The list sub-command produces a list of files present in the filesystem based on the file type specified.

###### Delete Sub-Command:

The delete sub-command deletes a single file object of the type specified from the filesystem.

###### Info Sub-Command:

The info sub-command returns information on the filesystem.

    bool WINC_CmdFSOP
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t op
        int32_t optFiletype
        const uint8_t* pOptFilename
        size_t lenOptFilename
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>op</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Operation.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>LIST</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DEL</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>INFO</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>optFiletype</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>File type.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>USER</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CERT</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PRIKEY</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DHPARAM</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>CFG</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table>
<p>optFiletype will be ignored if its value is<br />
WINC_CMDFSOP_FILETYPE_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pOptFilename</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>The name of the file.<br />
</p>
<p>Maximum length of string is 32<br />
</p>
<p>pOptFilename will be ignored if its value is NULL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptFilename</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pOptFilename.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                               | Description                    |
|----------------------------------------|--------------------------------|
| \<OP\>,\<FILETYPE\>,\<FILENAME\>       | List operation response        |
| \<OP\>,\<FREE_SPACE\>,\<FREE_HANDLES\> | Information operation response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OP&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>LOAD</p></td>
<td style="text-align: left;"><p>Load.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>LIST</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DEL</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>INFO</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>STORE</p></td>
<td style="text-align: left;"><p>Store.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILETYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>File type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>USER</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CERT</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PRIKEY</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DHPARAM</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>CFG</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>The name of the file<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_SPACE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Free space<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_HANDLES&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Free file handles<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdFSLOAD

##### Description

This function performs a filesystem operation.

This operation uses the WINC_CMD_ID_FS command request, therefore all status and response messages received will be using the WINC_CMD_ID_FS command ID. Messages are further identified by their \<OP\> response value indicating a value of 1.

    bool WINC_CmdFSLOAD
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t filetype
        const uint8_t* pOptFilename
        size_t lenOptFilename
        uint16_t optFilelength
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>filetype</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>File type.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>USER</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CERT</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PRIKEY</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DHPARAM</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>CFG</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>pOptFilename</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>The name of the file.<br />
</p>
<p>Maximum length of string is 32<br />
</p>
<p>pOptFilename will be ignored if its value is NULL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptFilename</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pOptFilename.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optFilelength</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>File length.<br />
</p>
<p>optFilelength will be ignored if its value is<br />
WINC_CMDFSLOAD_FILELENGTH_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response               | Description      |
|------------------------|------------------|
| \<OP\>,\<TSFR_HANDLE\> | FS-TSFR response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OP&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>LOAD</p></td>
<td style="text-align: left;"><p>Load.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>LIST</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DEL</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>INFO</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>STORE</p></td>
<td style="text-align: left;"><p>Store.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TSFR_HANDLE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Transfer handle<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_FS_FLFS_FSSTORE"></a>
#### WINC_CmdFSSTORE

##### Description

This function performs a filesystem operation.

This operation uses the WINC_CMD_ID_FS command request, therefore all status and response messages received will be using the WINC_CMD_ID_FS command ID. Messages are further identified by their \<OP\> response value indicating a value of 5.

    bool WINC_CmdFSSTORE
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t filetype
        const uint8_t* pFilename
        size_t lenFilename
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>filetype</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>File type.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>USER</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CERT</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PRIKEY</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DHPARAM</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>CFG</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>pFilename</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>The name of the file.<br />
</p>
<p>Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenFilename</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pFilename.<br />
</p></td>
</tr>
</tbody>
</table>

| Response               | Description      |
|------------------------|------------------|
| \<OP\>,\<TSFR_HANDLE\> | FS-TSFR response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OP&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>LOAD</p></td>
<td style="text-align: left;"><p>Load.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>LIST</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DEL</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>INFO</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>STORE</p></td>
<td style="text-align: left;"><p>Store.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TSFR_HANDLE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Transfer handle<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdFSTSFR

##### Description

This function performs a filesystem transfer operation.

    bool WINC_CmdFSTSFR
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t optTsfrHandle
        int32_t optBlockNum
        const uint8_t* pOptData
        size_t lenOptData
        int32_t optCrc
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optTsfrHandle</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>Transfer handle.<br />
</p>
<p>optTsfrHandle will be ignored if its value is<br />
WINC_CMDFSTSFR_TSFR_HANDLE_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optBlockNum</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Block number.<br />
</p>
<p>optBlockNum will be ignored if its value is<br />
WINC_CMDFSTSFR_BLOCK_NUM_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pOptData</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Transfer data.<br />
</p>
<p>pOptData will be ignored if its value is NULL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptData</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pOptData.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optCrc</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Transfer CRC-16.<br />
</p>
<p>optCrc will be ignored if its value is<br />
WINC_CMDFSTSFR_CRC_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<TSFR_HANDLE\>,\<BLOCK_NUM\>,\<BYTES_REMAIN\> | FS-TSFR load response |
| \<TSFR_HANDLE\>,\<BLOCK_NUM\>,\<BYTES_REMAIN\>,\<DATA\> | FS-TSFR store response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TSFR_HANDLE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Transfer handle<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BLOCK_NUM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Block number<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BYTES_REMAIN&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Bytes remaining<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Transfer data<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdFSRECV

##### Description

This function performs a filesystem transfer operation.

This transfer operation uses the WINC_CMD_ID_FSTSR command request, therefore all status and response messages received will be using the WINC_CMD_ID_FSTSFR command ID. Messages are further identified by their \<TSFR_HANDLE\> response value indicating transfer context used.

    bool WINC_CmdFSRECV
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t tsfrHandle
        uint8_t blockNum
        uint16_t optDataLength
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>tsfrHandle</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>Transfer handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>blockNum</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Block number.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optDataLength</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>Data length.<br />
</p>
<p>optDataLength will be ignored if its value is<br />
WINC_CMDFSRECV_DATA_LENGTH_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<TSFR_HANDLE\>,\<BLOCK_NUM\>,\<BYTES_REMAIN\> | FS-TSFR load response |
| \<TSFR_HANDLE\>,\<BLOCK_NUM\>,\<BYTES_REMAIN\>,\<DATA\> | FS-TSFR store response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TSFR_HANDLE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Transfer handle<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BLOCK_NUM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Block number<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BYTES_REMAIN&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Bytes remaining<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Transfer data<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_FS_FLFS_FSUP"></a>
#### WINC_AEC_ID_FSUP

##### Description

**Filesystem update.**

| AEC                                             | Description     |
|-------------------------------------------------|-----------------|
| \<OP\>,\<FILETYPE\>,\<FILENAME\>,\<FILELENGTH\> | Filesystem load |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OP&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>LOAD</p></td>
<td style="text-align: left;"><p>Load.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>LIST</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DEL</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>INFO</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>STORE</p></td>
<td style="text-align: left;"><p>Store.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILETYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>File type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>USER</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CERT</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PRIKEY</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DHPARAM</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>CFG</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>The name of the file<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILELENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>File length<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_9877579559e5e434da23523503bbceaaebdd6a80"></a>
**List and delete a file**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Request list of certificates
    APP->>API: WINC_CmdFSOP(2,1)
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"AmazonRootCA1")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"BaltimoreCyberTrustRoot")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"DigiCert")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"DigiCertGlobalRootG2")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"DigiCertSHA2")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"EnTrust")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"GlobalSignRoot")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"ISRGRootX1")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"QuoVadis_Root")
    API->>APP: Response:WINC_CMD_ID_FS(2,1,"VeriSign")
    API->>APP: Status:WINC_CMD_ID_FS(OK)
    Note right of APP: Delete certificate
    APP->>API: WINC_CmdFS(3,1,"AmazonRootCA1")
    API->>APP: Status:WINC_CMD_ID_FS(OK)
```

<a id="EXAMPLE_2e74f1ef2b6c2ef83ee4e90cb9de68a8a92de661"></a>
**Get filesystem information**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Request filesystem information
    APP->>API: WINC_CmdFSOP(4)
    Note left of API: 45056 bytes, 17 file handles free
    API->>APP: Response:WINC_CMD_ID_FS(4,45056,17)
    API->>APP: Status:WINC_CMD_ID_FS(OK)
```

<a id="EXAMPLE_0d368b631cc611ff30c1bc5a3025bc5aee1f7d59"></a>
**File load using FS-TSFR protocol**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Load certificate using FS_TSFR
    APP->>API: WINC_CmdFSLOAD(1,"ExampleCert",891)
    Note left of API: Certificate transfer handle
    API->>APP: Response:WINC_CMD_ID_FS(1,20489)
    API->>APP: Status:WINC_CMD_ID_FS(OK)
    Note right of APP: Send block 1, 128 bytes of data
    APP->>API: WINC_CmdFSTSFR(20489,1,[308203773082025F...7420526F6F74301E])
    Note left of API: Ack block 1, 763 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,1,763)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Send block 2, 128 bytes of data
    APP->>API: WINC_CmdFSTSFR(20489,2,[170D303030353132...6F7430820122300D])
    Note left of API: Ack block 2, 635 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,2,635)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Send block 3, 128 bytes of data
    APP->>API: WINC_CmdFSTSFR(20489,3,[06092A864886F70D...C328EAF5AB25878A])
    Note left of API: Ack block 3, 507 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,3,507)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Send block 4, 128 bytes of data
    APP->>API: WINC_CmdFSTSFR(20489,4,[9A961CA967B83F0C...BDC63AECE76E863A])
    Note left of API: Ack block 4, 379 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,4,379)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Send block 5, 128 bytes of data
    APP->>API: WINC_CmdFSTSFR(20489,5,[6B97746333BD6818...010100850C5D8EE4])
    Note left of API: Ack block 5, 251 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,5,251)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Send block 6, 128 bytes of data
    APP->>API: WINC_CmdFSTSFR(20489,6,[6F51684205A0DDBB...A9317A18BFA02AF4])
    Note left of API: Ack block 6, 123 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,6,123)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Send block 7, 123 bytes of data
    APP->>API: WINC_CmdFSTSFR(20489,7,[1299F7A34582E33C...6339A9])
    Note left of API: Ack block 7, no bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,7,0)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
```

<a id="EXAMPLE_a1c1b6e4bee3b5a03437950d9aaa8e7e4cced18f"></a>
**File store using FS-TSFR protocol**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Store certificate using FS-TSFR
    APP->>API: WINC_CmdFSSTORE(1,"ExampleCert")
    Note left of API: Certificate transfer handle
    API->>APP: Response:WINC_CMD_ID_FS(5,20489)
    API->>APP: Status:WINC_CMD_ID_FS(OK)
    Note right of APP: Get transfer report
    APP->>API: WINC_CmdFSTSFR(20489)
    Note left of API: No blocks sent, 891 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,0,891)
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Receive block 1, 128 bytes of data
    APP->>API: WINC_CmdFSRECV(20489,1,128)
    Note left of API: Block 1, 128 bytes, 763 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,1,763,[308203773082025F...7420526F6F74301E])
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Receive block 2, 128 bytes of data
    APP->>API: WINC_CmdFSRECV(20489,2,128)
    Note left of API: Block 2, 128 bytes, 635 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,2,635,[170D303030353132...6F7430820122300D])
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Receive block 3, 128 bytes of data
    APP->>API: WINC_CmdFSRECV(20489,3,128)
    Note left of API: Block 3, 128 bytes, 507 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,3,507,[06092A864886F70D...C328EAF5AB25878A])
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Receive block 4, 128 bytes of data
    APP->>API: WINC_CmdFSRECV(20489,4,128)
    Note left of API: Block 4, 128 bytes, 379 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,4,379,[9A961CA967B83F0C...BDC63AECE76E863A])
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Receive block 5, 128 bytes of data
    APP->>API: WINC_CmdFSRECV(20489,5,128)
    Note left of API: Block 5, 128 bytes, 251 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,5,251,[6B97746333BD6818...010100850C5D8EE4])
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Receive block 6, 128 bytes of data
    APP->>API: WINC_CmdFSRECV(20489,6,128)
    Note left of API: Block 6, 128 bytes, 123 bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,6,123,[6F51684205A0DDBB...A9317A18BFA02AF4])
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
    Note right of APP: Receive block 7, 123 bytes of data
    APP->>API: WINC_CmdFSRECV(20489,7,123)
    Note left of API: Block 7, 123 bytes, no bytes remain
    API->>APP: Response:WINC_CMD_ID_FSTSFR(20489,7,0,[1299F7A34582E33C5E...39A9])
    API->>APP: Status:WINC_CMD_ID_FSTSFR(OK)
```

---
<a id="AN_MOD_MQTT"></a>
## MQTT (Module ID = 8)

### Function Reference:

#### WINC_CmdMQTTC

##### Description

This function is used to read or set the MQTT configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdMQTTC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDMQTTC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_MQTT_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>BROKER_ADDR</p></td>
<td style="text-align: left;"><p>STRING<br />
IPV4ADDR<br />
IPV6ADDR<br />
</p></td>
<td style="text-align: left;"><p>Broker domain name or IP address<br />
Maximum length of string is 256<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
Format of IPv6 address is<br />
A1|…​|A16 = A1A2::A15A16<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>BROKER_PORT</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Broker listening TCP port<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>CLIENT_ID</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>MQTT client ID<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>USERNAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Username<br />
Maximum length of string is 128<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>PASSWORD</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Password<br />
Maximum length of string is 256<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>KEEP_ALIVE</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Keep alive time (in seconds)<br />
<br />
Valid range is 0 to 0x7FFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>TLS_CONF</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p>
<p>This parameter will only be visible to read if not zero.</p>
<p>Setting a value greater than zero enables TLS and makes this parameter visible.</p>
<p>Setting a value of zero disables TLS and makes this parameter hidden.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>PROTO_VER</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>MQTT protocol version, either 3 or 5<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>V3_1_1</p></td>
<td style="text-align: left;"><p>V3.1.1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>V5</p></td>
<td style="text-align: left;"><p>V5.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_MQTTC_STORE_ID_READ_THRESHOLD"></span> 9</p></td>
<td style="text-align: left;"><p>READ_THRESHOLD</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Subscription read threshold<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SOCKET_ID</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Socket ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTCONN

##### Description

This function is used to connect to an MQTT broker.

    bool WINC_CmdMQTTCONN
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optClean
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optClean</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Clean Session.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>USE_EXIST</p></td>
<td style="text-align: left;"><p>Use existing session, if available.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>USE_NEW</p></td>
<td style="text-align: left;"><p>Use new session.</p></td>
</tr>
</tbody>
</table>
<p>optClean will be ignored if its value is<br />
WINC_CMDMQTTCONN_CLEAN_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTSUB

##### Description

This function is used to subscribe to an MQTT topic.

    bool WINC_CmdMQTTSUB
    (
        WINC_CMD_REQ_HANDLE handle
        const uint8_t* pTopicName
        size_t lenTopicName
        uint8_t maxQos
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pTopicName</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Topic Name.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTopicName</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pTopicName.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>maxQos</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Maximum QoS.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QOS0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QOS1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QOS2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTSUBLST

##### Description

This function is used to list MQTT topic subscriptions.

**bool WINC_CmdMQTTSUBLST(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

| Response               | Description         |
|------------------------|---------------------|
| \<TOPIC_NAME\>,\<QOS\> | Subscription report |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QOS&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>QoS<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QOS0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QOS1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QOS2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_MQTT_MQTTSUBRD"></a>
#### WINC_CmdMQTTSUBRD

##### Description

This function is used receive data from subscriptions.

The [WINC_CmdMQTTSUBRD](#AN_FUNC_AT_MQTT_MQTTSUBRD) function is used in conjunction with the setting of [READ_THRESHOLD](#AN_FUNC_MQTTC_STORE_ID_READ_THRESHOLD).

When a message is received the API will emit a [WINC_AEC_ID_MQTTSUBRX](#AN_AEC_AT_MQTT_MQTTSUBRX) AEC, this will normally include the received data, however when a message is received which would exceed [READ_THRESHOLD](#AN_FUNC_MQTTC_STORE_ID_READ_THRESHOLD) the API will emit a [WINC_AEC_ID_MQTTSUBRX](#AN_AEC_AT_MQTT_MQTTSUBRX) AEC which includes a message ID and data length. This avoids saturating the application with data it may not be able to handle. The application must use this function to read the buffered message.

Setting [READ_THRESHOLD](#AN_FUNC_MQTTC_STORE_ID_READ_THRESHOLD) to zero will cause all received messages to be buffered for reading using this function.

> [!NOTE]
> The message ID is only relevant for QoS1 and QoS2 subscriptions.

    bool WINC_CmdMQTTSUBRD
    (
        WINC_CMD_REQ_HANDLE handle
        const uint8_t* pTopicName
        size_t lenTopicName
        uint16_t msgId
        uint16_t length
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pTopicName</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Topic Name.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTopicName</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pTopicName.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>msgId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>Message Identifier.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The number of bytes to receive.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                                    | Description          |
|---------------------------------------------|----------------------|
| \<MSG_ID\>,\<MSG_LENGTH\>,\<TOPIC_PAYLOAD\> | Read subscribed data |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;MSG_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Message ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MSG_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length of message<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Topic Payload<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTUNSUB

##### Description

This function is used to unsubscribe from an MQTT topic.

    bool WINC_CmdMQTTUNSUB
    (
        WINC_CMD_REQ_HANDLE handle
        const uint8_t* pTopicName
        size_t lenTopicName
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pTopicName</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Topic Name.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTopicName</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pTopicName.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTPUB

##### Description

This function is used to publish a message.

    bool WINC_CmdMQTTPUB
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t dup
        uint8_t qos
        uint8_t retain
        WINC_TYPE typeTopicNameId
        uintptr_t topicNameId
        size_t lenTopicNameId
        const uint8_t* pTopicPayload
        size_t lenTopicPayload
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>dup</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Duplicate Message.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NEW_MSG</p></td>
<td style="text-align: left;"><p>New message.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>DUP_MSG</p></td>
<td style="text-align: left;"><p>Duplicate message.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>qos</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>QoS.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QOS0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QOS1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QOS2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>retain</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Retain Message.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NOT_RETAINED</p></td>
<td style="text-align: left;"><p>Not retained on the server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>RETAINED</p></td>
<td style="text-align: left;"><p>Retained on the server.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeTopicNameId</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of topicNameId.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>topicNameId</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Topic Name or Alias.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTopicNameId</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of topicNameId.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pTopicPayload</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Topic Payload.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTopicPayload</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pTopicPayload.<br />
</p></td>
</tr>
</tbody>
</table>

| Response      | Description         |
|---------------|---------------------|
|               | Publish (QoS 0)     |
| \<PACKET_ID\> | Publish (QoS 1 & 2) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PACKET_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTLWT

##### Description

This function is used to define a last will message.

    bool WINC_CmdMQTTLWT
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t qos
        uint8_t retain
        const uint8_t* pTopicName
        size_t lenTopicName
        const uint8_t* pTopicPayload
        size_t lenTopicPayload
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>qos</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>QoS.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QOS0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QOS1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QOS2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>retain</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Retain Message.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NOT_RETAINED</p></td>
<td style="text-align: left;"><p>Not retained on the server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>RETAINED</p></td>
<td style="text-align: left;"><p>Retained on the server.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>pTopicName</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Topic Name.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTopicName</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pTopicName.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pTopicPayload</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Topic Payload.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTopicPayload</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pTopicPayload.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTDISCONN

##### Description

This function is used to disconnect from a broker.

    bool WINC_CmdMQTTDISCONN
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optReasonCode
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optReasonCode</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Reason Code.<br />
</p>
<p>optReasonCode will be ignored if its value is<br />
WINC_CMDMQTTDISCONN_REASON_CODE_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTPROPTX

##### Description

This function is used to read or set the MQTT transmit properties.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

Any defined and selected properties are added to transmitted MQTT packets. Only properties applicable to the MQTT packet type are added. Properties must be selected via the [WINC_CmdMQTTPROPTXS](#AN_FUNC_AT_MQTT_MQTTPROPTXS) function before they are included.

> [!NOTE]
> Not all properties listed below may be available in any implementation of this command set.

User property (38) supports multiple entries in the form of key/value pairs. If a key/value pair is specified for the command it will be added, if only a key is specified it will be removed.

    bool WINC_CmdMQTTPROPTX
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDMQTTPROPTX_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                | Description               |
|-------------------------|---------------------------|
| \<ID\>,\<VAL\>          | Read response             |
| \<ID\>,\<KEY\>,\<VALS\> | Read response (key/value) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_MQTT_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PAYLOAD_FORMAT_IND</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Payload Format Indicator<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>MSG_EXPIRY_INTERVAL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Message Expiry Interval<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>CONTENT_TYPE</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Content Type<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>RESP_TOPIC</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Response Topic<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>CORRELATION_DATA</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Correlation Data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SUBSCRIPTION_ID</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Subscription Identifier<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>17</p></td>
<td style="text-align: left;"><p>SESSION_EXPIRY_INTERVAL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Session Expiry Interval<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>23</p></td>
<td style="text-align: left;"><p>REQ_PROB_INFO</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Request Problem Information<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>24</p></td>
<td style="text-align: left;"><p>WILL_DELAY_INTERVAL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Will Delay Interval<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>25</p></td>
<td style="text-align: left;"><p>REQ_RESP_INFO</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Request Response Information<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>REASON_STR</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Reason String<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>RECEIVE_MAX</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Receive Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>TOPIC_ALIAS_MAX</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Topic Alias Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>35</p></td>
<td style="text-align: left;"><p>TOPIC_ALIAS</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Topic Alias<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>39</p></td>
<td style="text-align: left;"><p>MAX_PACKET_SZ</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Maximum Packet Size<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTPROPTXKV

##### Description

This function is used to read or set the MQTT transmit properties.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdMQTTPROPTXKV
    (
        WINC_CMD_REQ_HANDLE handle
        const uint8_t* pKey
        size_t lenKey
        const uint8_t* pOptVals
        size_t lenOptVals
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pKey</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Parameter key.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenKey</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pKey.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pOptVals</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p>
<p>pOptVals will be ignored if its value is NULL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVals</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pOptVals.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                | Description               |
|-------------------------|---------------------------|
| \<ID\>,\<VAL\>          | Read response             |
| \<ID\>,\<KEY\>,\<VALS\> | Read response (key/value) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_MQTT_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>38</p></td>
<td style="text-align: left;"><p>USER_PROP</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>User Property<br />
This is a multiple value parameter<br />
with an ID range 38.0 to 38.9<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTPROPRX

##### Description

This function is used to read or reset the MQTT receive properties.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

Any defined properties are added to transmitted MQTT packets. Only properties applicable to the MQTT packet type are added.

Any properties received are added to the list of available receive properties which can be queried by this command. Updates to the received properties are announced using the [WINC_AEC_ID_MQTTPROPRX](#AN_AEC_AT_MQTT_MQTTPROPRX) AEC and can be read via this command.

> [!NOTE]
> Not all properties listed below may be available in any implementation of this command set.

User property (38) supports multiple entries in the form of key/value pairs.

    bool WINC_CmdMQTTPROPRX
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDMQTTPROPRX_ID_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response                | Description               |
|-------------------------|---------------------------|
| \<ID\>,\<VAL\>          | Read response             |
| \<ID\>,\<KEY\>,\<VALS\> | Read response (key/value) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_MQTT_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PAYLOAD_FORMAT_IND</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Payload Format Indicator<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>MSG_EXPIRY_INTERVAL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Message Expiry Interval<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>CONTENT_TYPE</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Content Type<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>RESP_TOPIC</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Response Topic<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>CORRELATION_DATA</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Correlation Data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SUBSCRIPTION_ID</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Subscription Identifier<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>17</p></td>
<td style="text-align: left;"><p>SESSION_EXPIRY_INTERVAL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Session Expiry Interval<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>18</p></td>
<td style="text-align: left;"><p>ASSIGNED_CLIENT_ID</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Assigned Client Identifier<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>19</p></td>
<td style="text-align: left;"><p>SERVER_KEEP_ALIVE</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Server Keep Alive<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>23</p></td>
<td style="text-align: left;"><p>REQ_PROB_INFO</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Request Problem Information<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>25</p></td>
<td style="text-align: left;"><p>REQ_RESP_INFO</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Request Response Information<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>26</p></td>
<td style="text-align: left;"><p>RESP_INFO</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Response Information<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>28</p></td>
<td style="text-align: left;"><p>SERVER_REF</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Server Reference<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>REASON_STR</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Reason String<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>RECEIVE_MAX</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Receive Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>TOPIC_ALIAS_MAX</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Topic Alias Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>35</p></td>
<td style="text-align: left;"><p>TOPIC_ALIAS</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Topic Alias<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>36</p></td>
<td style="text-align: left;"><p>MAX_QOS</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Maximum QoS<br />
<br />
Valid range is 0 to 2<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>37</p></td>
<td style="text-align: left;"><p>RETAIN_AVAIL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Retain Available<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>38</p></td>
<td style="text-align: left;"><p>USER_PROP</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>User Property<br />
This is a multiple value parameter<br />
with an ID range 38.0 to 38.9<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>39</p></td>
<td style="text-align: left;"><p>MAX_PACKET_SZ</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Maximum Packet Size<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>WILDCARD_SUB_AVAIL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Wildcard Subscription Available<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>41</p></td>
<td style="text-align: left;"><p>SUBSCRIPTION_ID_AVAIL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Subscription Identifier Available<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>42</p></td>
<td style="text-align: left;"><p>SHARED_SUBSCRIPTION_AVAIL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Shared Subscription Available<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdMQTTPROPRXPRESET

##### Description

This function is used to read or reset the MQTT receive properties.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdMQTTPROPRXPRESET
    (
        WINC_CMD_REQ_HANDLE handle
        WINC_TYPE typeVal
        uintptr_t val
        size_t lenVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of val.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>val</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of val.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                | Description               |
|-------------------------|---------------------------|
| \<ID\>,\<VAL\>          | Read response             |
| \<ID\>,\<KEY\>,\<VALS\> | Read response (key/value) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_MQTT_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_MQTT_MQTTPROPTXS"></a>
#### WINC_CmdMQTTPROPTXS

##### Description

This function is used to define which transmit properties are selected.

    bool WINC_CmdMQTTPROPTXS
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optPropId
        int32_t optPropSel
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optPropId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Property Identifier.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>ALL</p></td>
<td style="text-align: left;"><p>All properties.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PAYLOAD_FORMAT_IND</p></td>
<td style="text-align: left;"><p>Payload Format Indicator.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>MSG_EXPIRY_INTERVAL</p></td>
<td style="text-align: left;"><p>Message Expiry Interval.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>CONTENT_TYPE</p></td>
<td style="text-align: left;"><p>Content Type.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>RESP_TOPIC</p></td>
<td style="text-align: left;"><p>Response Topic.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>CORRELATION_DATA</p></td>
<td style="text-align: left;"><p>Correlation Data.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SUBSCRIPTION_ID</p></td>
<td style="text-align: left;"><p>Subscription Identifier.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>17</p></td>
<td style="text-align: left;"><p>SESSION_EXPIRY_INTERVAL</p></td>
<td style="text-align: left;"><p>Session Expiry Interval.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>23</p></td>
<td style="text-align: left;"><p>REQ_PROB_INFO</p></td>
<td style="text-align: left;"><p>Request Problem Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>24</p></td>
<td style="text-align: left;"><p>WILL_DELAY_INTERVAL</p></td>
<td style="text-align: left;"><p>Will Delay Interval.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>25</p></td>
<td style="text-align: left;"><p>REQ_RESP_INFO</p></td>
<td style="text-align: left;"><p>Request Response Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>REASON_STR</p></td>
<td style="text-align: left;"><p>Reason String.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>RECEIVE_MAX</p></td>
<td style="text-align: left;"><p>Receive Maximum.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>TOPIC_ALIAS_MAX</p></td>
<td style="text-align: left;"><p>Topic Alias Maximum.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>35</p></td>
<td style="text-align: left;"><p>TOPIC_ALIAS</p></td>
<td style="text-align: left;"><p>Topic Alias.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>38</p></td>
<td style="text-align: left;"><p>USER_PROP</p></td>
<td style="text-align: left;"><p>User Property.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>39</p></td>
<td style="text-align: left;"><p>MAX_PACKET_SZ</p></td>
<td style="text-align: left;"><p>Maximum Packet Size.</p></td>
</tr>
</tbody>
</table>
<p>optPropId will be ignored if its value is<br />
WINC_CMDMQTTPROPTXS_PROP_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optPropSel</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Property Selected.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PROP_NOT_SEL</p></td>
<td style="text-align: left;"><p>Property not selected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PROP_SEL</p></td>
<td style="text-align: left;"><p>Property is selected.</p></td>
</tr>
</tbody>
</table>
<p>optPropSel will be ignored if its value is<br />
WINC_CMDMQTTPROPTXS_PROP_SEL_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response                 | Description   |
|--------------------------|---------------|
| \<PROP_ID\>,\<PROP_SEL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PROP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Property Identifier<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROP_SEL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Property Selected<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NOT_SELECTED</p></td>
<td style="text-align: left;"><p>Property not selected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SELECTED</p></td>
<td style="text-align: left;"><p>Property is selected.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_MQTTCONN

##### Description

**Connection state.**

| AEC            | Description      |
|----------------|------------------|
| \<CONN_STATE\> | Connection state |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONN_STATE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>MQTT connected state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NOT_CONNECTED</p></td>
<td style="text-align: left;"><p>Not connected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CONNECTED</p></td>
<td style="text-align: left;"><p>Connected.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_MQTTCONNACK

##### Description

**Connection acknowledge.**

| AEC                                    | Description      |
|----------------------------------------|------------------|
| \<CONNACK_FLAGS\>,\<CONN_REASON_CODE\> | Connection state |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONNACK_FLAGS&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Connect acknowledge flags<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NO_SESSION</p></td>
<td style="text-align: left;"><p>No session.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SESSION_PRESENT</p></td>
<td style="text-align: left;"><p>Session present.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CONN_REASON_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Connect reason code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>SUCCESS</p></td>
<td style="text-align: left;"><p>Success.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>128</p></td>
<td style="text-align: left;"><p>ERROR</p></td>
<td style="text-align: left;"><p>Unspecified error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>129</p></td>
<td style="text-align: left;"><p>MALFORM_PKT</p></td>
<td style="text-align: left;"><p>Malformed packet.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>130</p></td>
<td style="text-align: left;"><p>PROT_ERR</p></td>
<td style="text-align: left;"><p>Protocol error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>131</p></td>
<td style="text-align: left;"><p>IMP_SPEC_ERR</p></td>
<td style="text-align: left;"><p>Implementation specific error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>132</p></td>
<td style="text-align: left;"><p>PROT_NA</p></td>
<td style="text-align: left;"><p>Unsupported protocol version.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>133</p></td>
<td style="text-align: left;"><p>INVALID_CLIENT_ID</p></td>
<td style="text-align: left;"><p>Client identifier not valid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>134</p></td>
<td style="text-align: left;"><p>BAD_USER_PASS</p></td>
<td style="text-align: left;"><p>Bad username or password.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>135</p></td>
<td style="text-align: left;"><p>NOT_AUTH</p></td>
<td style="text-align: left;"><p>Not authorized.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>136</p></td>
<td style="text-align: left;"><p>SRV_NA</p></td>
<td style="text-align: left;"><p>Server unavailable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>137</p></td>
<td style="text-align: left;"><p>SRV_BUSY</p></td>
<td style="text-align: left;"><p>Server busy.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>138</p></td>
<td style="text-align: left;"><p>BANNED</p></td>
<td style="text-align: left;"><p>Banned.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>140</p></td>
<td style="text-align: left;"><p>BAD_AUTH</p></td>
<td style="text-align: left;"><p>Bad authentication method.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>144</p></td>
<td style="text-align: left;"><p>TOP_INVALID</p></td>
<td style="text-align: left;"><p>Topic name invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>149</p></td>
<td style="text-align: left;"><p>PKT_TOO_LARGE</p></td>
<td style="text-align: left;"><p>Packet too large.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>151</p></td>
<td style="text-align: left;"><p>QUOTA_EXCEED</p></td>
<td style="text-align: left;"><p>Quota exceeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>153</p></td>
<td style="text-align: left;"><p>PAYLOAD_INVALID</p></td>
<td style="text-align: left;"><p>Payload format invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>154</p></td>
<td style="text-align: left;"><p>RETAIN_NA</p></td>
<td style="text-align: left;"><p>Retain not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>155</p></td>
<td style="text-align: left;"><p>QOS_NA</p></td>
<td style="text-align: left;"><p>QoS not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>156</p></td>
<td style="text-align: left;"><p>USE_DIFF_SRV</p></td>
<td style="text-align: left;"><p>Use another server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>156</p></td>
<td style="text-align: left;"><p>SRV_MOVED</p></td>
<td style="text-align: left;"><p>Server moved.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>159</p></td>
<td style="text-align: left;"><p>CONN_RATE_EXCEED</p></td>
<td style="text-align: left;"><p>Connection rate exceeded.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_MQTTPUBACK

##### Description

**Publish acknowledge.**

| AEC           | Description         |
|---------------|---------------------|
| \<PACKET_ID\> | Publish acknowledge |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PACKET_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_MQTTPUBCOMP

##### Description

**Publish complete.**

| AEC           | Description      |
|---------------|------------------|
| \<PACKET_ID\> | Publish complete |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PACKET_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_MQTTPUBERR

##### Description

**Publish error.**

| AEC           | Description   |
|---------------|---------------|
| \<PACKET_ID\> | Publish error |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PACKET_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_MQTTSUB

##### Description

**Subscribe response.**

| AEC             | Description        |
|-----------------|--------------------|
| \<REASON_CODE\> | Subscribe response |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;REASON_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>SUBACK return code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QOS0_GRANTED</p></td>
<td style="text-align: left;"><p>Granted QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QOS1_GRANTED</p></td>
<td style="text-align: left;"><p>Granted QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QOS2_GRANTED</p></td>
<td style="text-align: left;"><p>Granted QoS 2.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>128</p></td>
<td style="text-align: left;"><p>ERROR</p></td>
<td style="text-align: left;"><p>Unspecified error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>131</p></td>
<td style="text-align: left;"><p>IMP_SPEC_ERR</p></td>
<td style="text-align: left;"><p>Implementation specific error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>135</p></td>
<td style="text-align: left;"><p>NOT_AUTH</p></td>
<td style="text-align: left;"><p>Not authorized.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>143</p></td>
<td style="text-align: left;"><p>TOP_FILT_INVALID</p></td>
<td style="text-align: left;"><p>Topic filter invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>145</p></td>
<td style="text-align: left;"><p>PKT_ID_IN_USE</p></td>
<td style="text-align: left;"><p>Packet identifier in use.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>151</p></td>
<td style="text-align: left;"><p>QUOTA_EXCEED</p></td>
<td style="text-align: left;"><p>Quota exceeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>158</p></td>
<td style="text-align: left;"><p>SHARED_SUB_NOT_SUP</p></td>
<td style="text-align: left;"><p>Shared Subscriptions not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>161</p></td>
<td style="text-align: left;"><p>SUB_IDENT_NA</p></td>
<td style="text-align: left;"><p>Subscription identifiers not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>162</p></td>
<td style="text-align: left;"><p>WILDCARD_SUB_NA</p></td>
<td style="text-align: left;"><p>Wildcard subscriptions not supported.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_MQTTUNSUB

##### Description

**Unsubscribe response.**

| AEC        | Description          |
|------------|----------------------|
| \<RESULT\> | Unsubscribe response |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;RESULT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Result of unsubscribe request<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>SUCCESS</p></td>
<td style="text-align: left;"><p>Success.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>NO_SUB</p></td>
<td style="text-align: left;"><p>No subscription existed.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>128</p></td>
<td style="text-align: left;"><p>ERROR</p></td>
<td style="text-align: left;"><p>Unspecified error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>131</p></td>
<td style="text-align: left;"><p>IMP_SPEC_ERR</p></td>
<td style="text-align: left;"><p>Implementation specific error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>135</p></td>
<td style="text-align: left;"><p>NOT_AUTH</p></td>
<td style="text-align: left;"><p>Not authorized.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>143</p></td>
<td style="text-align: left;"><p>TOP_FILT_INVALID</p></td>
<td style="text-align: left;"><p>Topic filter invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>145</p></td>
<td style="text-align: left;"><p>PKT_ID_IN_USE</p></td>
<td style="text-align: left;"><p>Packet identifier in use.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_MQTT_MQTTSUBRX"></a>
#### WINC_AEC_ID_MQTTSUBRX

##### Description

**Receive subscribed data.**

| AEC | Description |
|----|----|
| \<DUP\>,\<QOS\>,\<RETAIN\>,\<TOPIC_NAME\>,\<TOPIC_PAYLOAD\> | Received subscribed data |
| \<DUP\>,\<QOS\>,\<RETAIN\>,\<TOPIC_NAME\>,\<MSG_ID\>,\<MSG_LENGTH\> | Received subscribed data notification |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;DUP&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Duplicate Message<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NEW_MSG</p></td>
<td style="text-align: left;"><p>New message.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>DUP_MSG</p></td>
<td style="text-align: left;"><p>Duplicate message.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QOS&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>QoS<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QOS0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QOS1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QOS2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RETAIN&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Retain Message<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NOT_RETAINED</p></td>
<td style="text-align: left;"><p>Not retained on the server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>RETAINED</p></td>
<td style="text-align: left;"><p>Retained on the server.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Topic Payload<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MSG_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Message ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MSG_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length of message<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_MQTT_MQTTPROPRX"></a>
#### WINC_AEC_ID_MQTTPROPRX

##### Description

**Indicates property has been updated.**

| AEC                          | Description                              |
|------------------------------|------------------------------------------|
| \<PROP_ID\>                  | Property ID updated                      |
| \<PROP_ID\>,\<VAL\>          | Property ID updated, with value          |
| \<PROP_ID\>,\<KEY\>,\<VALS\> | Property ID updated, with key/value pair |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PROP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Property Identifier<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_763df688af86d232581b5749c292a4aadffbdcd4"></a>
**MQTT connection directly over TLS**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note left of API: Wait for time for correct TLS operation
    API->>APP: AEC:WINC_AEC_ID_TIME(3969510079)
    Note right of APP: Set the broker CA certificate
    APP->>API: WINC_CmdTLSC(1,1,"ServerCACert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set the broker domain
    APP->>API: WINC_CmdTLSC(1,6,"example.com")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set the broker hostname
    APP->>API: WINC_CmdMQTTC(1,"mqtt.example.com")
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Set the MQTTS port number
    APP->>API: WINC_CmdMQTTC(2,8883)
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Set client ID
    APP->>API: WINC_CmdMQTTC(3,"clientid")
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Set username
    APP->>API: WINC_CmdMQTTC(4,"username")
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Set password
    APP->>API: WINC_CmdMQTTC(5,"password")
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Use TLSC index 1
    APP->>API: WINC_CmdMQTTC(7,1)
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Connect to broker
    APP->>API: WINC_CmdMQTTCONN(1)
    API->>APP: Status:WINC_CMD_ID_MQTTCONN(OK)
    Note left of API: Received property Topic Alias Max=10
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(34,10)
    Note left of API: Received property Receive Max=20
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(33,20)
    Note left of API: CONNACK response
    API->>APP: AEC:WINC_AEC_ID_MQTTCONNACK(0,0)
    Note left of API: Connected
    API->>APP: AEC:WINC_AEC_ID_MQTTCONN(1)
```

<a id="EXAMPLE_8cb9b789fe72ee96a4f00e56c7528fefed94d312"></a>
**MQTT connection over TLS socket**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note left of API: Wait for time for correct TLS operation
    API->>APP: AEC:WINC_AEC_ID_TIME(3969510551)
    Note right of APP: Open TCP socket
    APP->>API: WINC_CmdSOCKO(2)
    API->>APP: Response:WINC_CMD_ID_SOCKO(17604)
    API->>APP: Status:WINC_CMD_ID_SOCKO(OK)
    Note right of APP: Set the broker CA certificate
    APP->>API: WINC_CmdTLSC(1,1,"ServerCACert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set the broker domain
    APP->>API: WINC_CmdTLSC(1,6,"example.com")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set client ID
    APP->>API: WINC_CmdMQTTC(3,"clientid")
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Set username
    APP->>API: WINC_CmdMQTTC(4,"username")
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Set password
    APP->>API: WINC_CmdMQTTC(5,"password")
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Assign socket ID to MQTT configuration
    APP->>API: WINC_CmdMQTTC(10,17604)
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note right of APP: Upgrade socket to TLS
    APP->>API: WINC_CmdSOCKTLS(17604,1)
    API->>APP: Status:WINC_CMD_ID_SOCKTLS(OK)
    Note right of APP: Bind socket to server
    APP->>API: WINC_CmdSOCKBR(17604,"mqtt.example.com",8883)
    API->>APP: Status:WINC_CMD_ID_SOCKBR(OK)
    Note left of API: Socket connected
    API->>APP: AEC:WINC_AEC_ID_SOCKIND(17604,"1.2.3.4",65333,"5.6.7.8",8883)
    Note left of API: Socket upgraded to TLS
    API->>APP: AEC:WINC_AEC_ID_SOCKTLS(17604)
    Note right of APP: Connect to broker
    APP->>API: WINC_CmdMQTTCONN(1)
    API->>APP: Status:WINC_CMD_ID_MQTTCONN(OK)
    Note left of API: Received property Topic Alias Max=10
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(34,10)
    Note left of API: Received property Receive Max=20
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(33,20)
    Note left of API: CONNACK response
    API->>APP: AEC:WINC_AEC_ID_MQTTCONNACK(0,0)
    Note left of API: Connected
    API->>APP: AEC:WINC_AEC_ID_MQTTCONN(1)
```

<a id="EXAMPLE_520a41f5f278cbdca5ec88603f0abace550e4c65"></a>
**Subscribe to MQTT topic and receive data (asynchronously)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Subscribe to topic with QoS=1
    APP->>API: WINC_CmdMQTTSUB("Topic/name",1)
    API->>APP: Status:WINC_CMD_ID_MQTTSUB(OK)
    Note left of API: Subscription granted QoS=1
    API->>APP: AEC:WINC_AEC_ID_MQTTSUB(1)
    Note left of API: Message property 1 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(1,0)
    Note left of API: Message property 3 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(3,"text/plain")
    Note left of API: Message received with data
    API->>APP: AEC:WINC_AEC_ID_MQTTSUBRX(0,1,0,"Topic/name","ExampleText1")
    Note left of API: Message property 1 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(1,0)
    Note left of API: Message property 3 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(3,"text/plain")
    Note left of API: Message received with data
    API->>APP: AEC:WINC_AEC_ID_MQTTSUBRX(0,1,0,"Topic/name","ExampleText2")
```

<a id="EXAMPLE_e86e402f305e460d8856aba5d60360834676ed35"></a>
**Subscribe to MQTT topic and receive data (polled)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Subscribe to topic with QoS=1
    APP->>API: WINC_CmdMQTTSUB("Topic/name",1)
    API->>APP: Status:WINC_CMD_ID_MQTTSUB(OK)
    Note left of API: Subscription granted QoS=1
    API->>APP: AEC:WINC_AEC_ID_MQTTSUB(1)
    Note right of APP: Configure receive threshold to zero bytes
    APP->>API: WINC_CmdMQTTC(9,0)
    API->>APP: Status:WINC_CMD_ID_MQTTC(OK)
    Note left of API: Message property 1 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(1,0)
    Note left of API: Message property 3 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(3,"text/plain")
    Note left of API: Message received, ID=1, length=12
    API->>APP: AEC:WINC_AEC_ID_MQTTSUBRX(0,1,0,"Topic/name",1,12)
    Note left of API: Message property 1 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(1,0)
    Note left of API: Message property 3 received
    API->>APP: AEC:WINC_AEC_ID_MQTTPROPRX(3,"text/plain")
    Note left of API: Message received, ID=2, length=12
    API->>APP: AEC:WINC_AEC_ID_MQTTSUBRX(0,1,0,"Topic/name",2,12)
    Note right of APP: Read message ID=1
    APP->>API: WINC_CmdMQTTSUBRD("Topic/name",1,12)
    Note left of API: Message ID=1 data
    API->>APP: Response:WINC_CMD_ID_MQTTSUBRD(11,"ExampleText1")
    Note right of APP: Read message ID=2
    APP->>API: WINC_CmdMQTTSUBRD("Topic/name",2,12)
    Note left of API: Message ID=2 data
    API->>APP: Response:WINC_CMD_ID_MQTTSUBRD(11,"ExampleText2")
```

---
<a id="AN_MOD_NETIF"></a>
## NETIF (Module ID = 9)

### Function Reference:

#### WINC_CmdNETIFC

##### Description

This function is used to read or set the network interface configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdNETIFC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optIntf
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optIntf</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Interface number.<br />
</p>
<p>optIntf will be ignored if its value is<br />
WINC_CMDNETIFC_INTF_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDNETIFC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response          | Description   |
|-------------------|---------------|
| \<INTF\>,\<INTF\> | List response |
| \<ID\>,\<VAL\>    | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;INTF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Interface number<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_NETIF_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Network interface name<br />
Maximum length of string is 16<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>ETHER</p></td>
<td style="text-align: left;"><p>MACADDR<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Ethernet MAC address of interface<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>HOSTNAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Name of this interface<br />
Maximum length of string is 16<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>DHCPC_EN</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>DHCP client enable<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Disabled - use static configuration.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Enabled - use automatic settings.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>DHCPC_LEASE_START</p></td>
<td style="text-align: left;"><p>UTC_TIME<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>DHCP lease start time, displayed in system time format<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>DHCPC_LEASE_ENDS</p></td>
<td style="text-align: left;"><p>UTC_TIME<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>DHCP lease end time, displayed in system time format<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>DHCPC_SRV_ADDR</p></td>
<td style="text-align: left;"><p>IPV4ADDR<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>IP address of DHCP server<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>L2_ONLY</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Layer 2 only flag<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>LAYER3</p></td>
<td style="text-align: left;"><p>Layer 3 active.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>LAYER2</p></td>
<td style="text-align: left;"><p>Layer 3 not active.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>L2_MONITOR_MODE</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>L2 monitor mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OFF</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UNICAST</p></td>
<td style="text-align: left;"><p>Unicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>BCAST</p></td>
<td style="text-align: left;"><p>Broadcast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>UNI_BCAST</p></td>
<td style="text-align: left;"><p>Unicast + Broadcast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>MCAST</p></td>
<td style="text-align: left;"><p>Multicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>UNI_MCAST</p></td>
<td style="text-align: left;"><p>Unicast + Multicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>B_MCAST</p></td>
<td style="text-align: left;"><p>Broadcast + Multicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>UNI_B_MCAST</p></td>
<td style="text-align: left;"><p>Unicast + Broadcast + Multicast.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>L2_MONITOR_MAX_LEN</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>L2 monitor max length<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>IP_MASK</p></td>
<td style="text-align: left;"><p>IPV4ADDR<br />
</p></td>
<td style="text-align: left;"><p>IP address and net mask<br />
Format of IPv4 address and netmask is<br />
A1|A2|A3|A4|M1|M2|M3|M4 = A1.A2.A3.A4 + M1.M2.M3.M4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>41</p></td>
<td style="text-align: left;"><p>GATEWAY</p></td>
<td style="text-align: left;"><p>IPV4ADDR<br />
</p></td>
<td style="text-align: left;"><p>IP address of gateway<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>60</p></td>
<td style="text-align: left;"><p>IPV6_GLO_ADDR</p></td>
<td style="text-align: left;"><p>IPV6ADDR<br />
</p></td>
<td style="text-align: left;"><p>IPv6 global address<br />
Format of IPv6 address and scope is<br />
A1|…​|A16 | M1 = A1A2::A15A16/M1<br />
This is a multiple value parameter<br />
with an ID range 60.0 to 60.1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>61</p></td>
<td style="text-align: left;"><p>IPV6_LL_ADDR</p></td>
<td style="text-align: left;"><p>IPV6ADDR<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>IPv6 link-local address<br />
Format of IPv6 address and scope is<br />
A1|…​|A16 | M1 = A1A2::A15A16/M1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>62</p></td>
<td style="text-align: left;"><p>IPV6_GATEWAY</p></td>
<td style="text-align: left;"><p>IPV6ADDR<br />
</p></td>
<td style="text-align: left;"><p>IPv6 gateway address<br />
Format of IPv6 address is<br />
A1|…​|A16 = A1A2::A15A16<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdNETIFTX

##### Description

This function is used to send L2 data frames.

    bool WINC_CmdNETIFTX
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t intf
        const uint8_t* pData
        size_t lenData
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>intf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Interface number.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pData</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Data frame data.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenData</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pData.<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_NETIFRX

##### Description

**Received L2 data frame.**

| AEC                               | Description   |
|-----------------------------------|---------------|
| \<INTF\>,\<DATA_LENGTH\>,\<DATA\> | L2 data frame |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;INTF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Interface number<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Data frame<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_OTA"></a>
## OTA (Module ID = 10)

### Function Reference:

#### WINC_CmdOTAC

##### Description

This function is used to read or set the OTA configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdOTAC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDOTAC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_OTA_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PROTOCOL</p></td>
<td style="text-align: left;"><p>INTEGER<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Protocol type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>HTTP</p></td>
<td style="text-align: left;"><p>HTTP.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>HOST</p></td>
<td style="text-align: left;"><p>STRING<br />
IPV4ADDR<br />
IPV6ADDR<br />
</p></td>
<td style="text-align: left;"><p>Host domain name or IP address<br />
Maximum length of string is 255<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
Format of IPv6 address is<br />
A1|…​|A16 = A1A2::A15A16<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>PORT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Listening port<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>PATH</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Path to firmware<br />
Maximum length of string is 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>FILE</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Firmware file<br />
Maximum length of string is 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>TIMEOUT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Timeout in seconds<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>TLS_CONF</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SOCKET_ID</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Socket ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdOTADL

##### Description

This function allows the downloading of firmware to the WINC.

    bool WINC_CmdOTADL
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t state
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>state</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Enable the OTA download feature.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLE</p></td>
<td style="text-align: left;"><p>Use configuration from WINC_CmdOTAC command.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response      | Description           |
|---------------|-----------------------|
| \<OTA_OP_ID\> | OTA download response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OTA_OP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdOTAVFY

##### Description

This function verifies the OTA firmware image.

**bool WINC_CmdOTAVFY(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

| Response      | Description         |
|---------------|---------------------|
| \<OTA_OP_ID\> | OTA verify response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OTA_OP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdOTAACT

##### Description

This function activates the OTA firmware image.

**bool WINC_CmdOTAACT(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

| Response      | Description           |
|---------------|-----------------------|
| \<OTA_OP_ID\> | OTA activate response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OTA_OP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdOTAINV

##### Description

This function will invalidate the current running firmware image. Invalidation does not delete the current running firmware image.

**bool WINC_CmdOTAINV(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

| Response      | Description             |
|---------------|-------------------------|
| \<OTA_OP_ID\> | OTA invalidate response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OTA_OP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_OTA

##### Description

**OTA state.**

| AEC                         | Description |
|-----------------------------|-------------|
| \<OTA_OP_ID\>,\<OTA_STATE\> | OTA status  |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OTA_OP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OTA_STATE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Status code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>ERASE_DONE</p></td>
<td style="text-align: left;"><p>Erase done.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>WRITE_DONE</p></td>
<td style="text-align: left;"><p>Write done.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>VERIFY_DONE</p></td>
<td style="text-align: left;"><p>Verify done.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>ACTIVATE_DONE</p></td>
<td style="text-align: left;"><p>Activate done.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_OTAERR

##### Description

**OTA error.**

| AEC                          | Description |
|------------------------------|-------------|
| \<OTA_OP_ID\>,\<ERROR_CODE\> | OTA error   |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OTA_OP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_OTA_HTTP_CONF"></a>
**Internal OTA HTTP Configuration**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Set host
    APP->>API: WINC_CmdOTAC(2,"example.com")
    API->>APP: Status:WINC_CMD_ID_OTAC(OK)
    Note right of APP: Set port
    APP->>API: WINC_CmdOTAC(3,80)
    API->>APP: Status:WINC_CMD_ID_OTAC(OK)
    Note right of APP: Set path
    APP->>API: WINC_CmdOTAC(4,"/firmware/")
    API->>APP: Status:WINC_CMD_ID_OTAC(OK)
    Note right of APP: Set filename
    APP->>API: WINC_CmdOTAC(5,"rnwf02_ota.bootable.bin")
    API->>APP: Status:WINC_CMD_ID_OTAC(OK)
```

<a id="EXAMPLE_OTA_HTTPS_CONF"></a>
**Internal OTA HTTPS Configuration**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Set TLS configuration
    APP->>API: WINC_CmdOTAC(7,1)
    API->>APP: Status:WINC_CMD_ID_OTAC(OK)
```

<a id="EXAMPLE_OTA_INTERNAL"></a>
**Internal OTA**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Request OTA download
    APP->>API: WINC_CmdOTADL(1)
    API->>APP: Response:WINC_CMD_ID_OTADL(1)
    API->>APP: Status:WINC_CMD_ID_OTADL(OK)
    Note left of API: Partiton erased AEC
    API->>APP: AEC:WINC_AEC_ID_OTA(1,10.0,"Erase Done")
    Note left of API: Firmware image written AEC
    API->>APP: AEC:WINC_AEC_ID_OTA(1,10.1,"Write Done")
    Note left of API: Firmware image verified AEC
    API->>APP: AEC:WINC_AEC_ID_OTA(1,10.2,"Verify Done")
    Note right of APP: Request to activate firmware
    APP->>API: WINC_CmdOTAACT()
    API->>APP: Response:WINC_CMD_ID_OTAACT(2)
    API->>APP: Status:WINC_CMD_ID_OTAACT(OK)
    Note left of API: Activation successful AEC
    API->>APP: AEC:WINC_AEC_ID_OTA(2,10.3,"Activate Done")
```

<a id="EXAMPLE_OTA_NVM"></a>
**NVM OTA**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Write firmware image data
    APP->>API: WINC_CmdNVMWR(0,512,[FFFFFFFF0101E0005048434D0300000000000300FFFFFFFF...])
    API->>APP: Status:WINC_CMD_ID_NVMWR(OK)
    APP->>API: WINC_CmdNVMWR(0,512,[...])
    API->>APP: Status:WINC_CMD_ID_NVMWR(OK)
    Note right of APP: Request to verify firmware image
    APP->>API: WINC_CmdOTAVFY()
    API->>APP: Response:WINC_CMD_ID_OTAVFY(1)
    API->>APP: Status:WINC_CMD_ID_OTAVFY(OK)
    Note left of API: Firmware image verified AEC
    API->>APP: AEC:WINC_AEC_ID_OTA(1,10.2,"Verify Done")
    Note right of APP: Request to activate firmware
    APP->>API: WINC_CmdOTAACT()
    API->>APP: Response:WINC_CMD_ID_OTAACT(2)
    API->>APP: Status:WINC_CMD_ID_OTAACT(OK)
    Note left of API: Activation successful AEC
    API->>APP: AEC:WINC_AEC_ID_OTA(2,10.3,"Activate Done")
```

---
<a id="AN_MOD_PING"></a>
## PING (Module ID = 11)

### Function Reference:

#### WINC_CmdPING

##### Description

This function sends a ping (ICMP Echo Request) to the target address.

    bool WINC_CmdPING
    (
        WINC_CMD_REQ_HANDLE handle
        WINC_TYPE typeTargetAddr
        uintptr_t targetAddr
        size_t lenTargetAddr
        uint8_t optProtocolVersion
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeTargetAddr</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of targetAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>targetAddr</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>IP address or host name of target.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenTargetAddr</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of targetAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optProtocolVersion</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>IP protocol version.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>IPV4</p></td>
<td style="text-align: left;"><p>IPv4.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>IPV6</p></td>
<td style="text-align: left;"><p>IPv6.</p></td>
</tr>
</tbody>
</table>
<p>optProtocolVersion will be ignored if its value is<br />
WINC_CMDPING_PROTOCOL_VERSION_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_PING

##### Description

**Successful ping.**

| AEC                    | Description           |
|------------------------|-----------------------|
| \<IP_ADDRESS\>,\<RTT\> | Ping success response |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;IP_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>IP address of the target<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RTT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Round trip time (in milliseconds)<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_PINGERR

##### Description

**Error.**

| AEC            | Description |
|----------------|-------------|
| \<ERROR_CODE\> | Ping error  |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
## RST (Module ID = 12)

### Function Reference:

#### WINC_CmdRST

##### Description

This function is used to reset the WINC.

**bool WINC_CmdRST(WINC_CMD_REQ_HANDLE handle)**

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
</tbody>
</table>

---
---
<a id="AN_MOD_SNTP"></a>
## SNTP (Module ID = 13)

### Function Reference:

#### WINC_CmdSNTPC

##### Description

This function is used to read or set the SNTP configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdSNTPC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDSNTPC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_SNTP_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>NTP_ENABLED</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Network Time (NTP) client function<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISBLED</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>NTP_STATIC</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>NTP configuration mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>AUTO</p></td>
<td style="text-align: left;"><p>Auto-assigned by network.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>MANUAL</p></td>
<td style="text-align: left;"><p>Manually configured by user.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>NTP_SVR</p></td>
<td style="text-align: left;"><p>STRING<br />
IPV4ADDR<br />
IPV6ADDR<br />
</p></td>
<td style="text-align: left;"><p>The address/name of NTP server<br />
Maximum length of string is 128<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
Format of IPv6 address is<br />
A1|…​|A16 = A1A2::A15A16<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_SNTPERR

##### Description

**SNTP error.**

| AEC            | Description |
|----------------|-------------|
| \<ERROR_CODE\> | SNTP error  |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_SOCKET"></a>
## SOCKET (Module ID = 14)

### Function Reference:

#### WINC_CmdSOCKO

##### Description

This function is used to open a new socket.

    bool WINC_CmdSOCKO
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t protocol
        uint8_t optProtocolVersion
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>protocol</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>The protocol to use.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UDP</p></td>
<td style="text-align: left;"><p>UDP.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>TCP</p></td>
<td style="text-align: left;"><p>TCP.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>optProtocolVersion</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>IP protocol version.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>IPV4</p></td>
<td style="text-align: left;"><p>IPv4.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>IPV6</p></td>
<td style="text-align: left;"><p>IPv6.</p></td>
</tr>
</tbody>
</table>
<p>optProtocolVersion will be ignored if its value is<br />
WINC_CMDSOCKO_PROTOCOL_VERSION_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response    | Description          |
|-------------|----------------------|
| \<SOCK_ID\> | Socket open response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKBL

##### Description

This function is used to bind a socket to a local port.

    bool WINC_CmdSOCKBL
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        uint16_t lclPort
        uint8_t optPendSkts
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lclPort</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The local port number to use.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optPendSkts</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Number of pending sockets connections.<br />
</p>
<p>optPendSkts will be ignored if its value is<br />
WINC_CMDSOCKBL_PEND_SKTS_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKBR

##### Description

This function is used to bind a socket to a remote address.

    bool WINC_CmdSOCKBR
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        WINC_TYPE typeRmtAddr
        uintptr_t rmtAddr
        size_t lenRmtAddr
        uint16_t rmtPort
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeRmtAddr</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of rmtAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>rmtAddr</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>The address of the remote device.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenRmtAddr</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of rmtAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>rmtPort</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The port number on the remote device.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKBM

##### Description

This function is used to bind a socket to a multicast group.

    bool WINC_CmdSOCKBM
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        WINC_TYPE typeMcastAddr
        uintptr_t mcastAddr
        size_t lenMcastAddr
        uint16_t mcastPort
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeMcastAddr</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of mcastAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>mcastAddr</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>The address of the multicast group.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenMcastAddr</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of mcastAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>mcastPort</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The port number of the multicast group.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKTLS

##### Description

This function is used to enable TLS on a socket.

    bool WINC_CmdSOCKTLS
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        uint8_t tlsConf
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>tlsConf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>TLS certificate configuration.<br />
</p></td>
</tr>
</tbody>
</table>

| Response    | Description |
|-------------|-------------|
| \<SOCK_ID\> | TLS succeed |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKWR

##### Description

This function is used to send data over a socket that is bound to a remote address and port number.

    bool WINC_CmdSOCKWR
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        uint16_t length
        int32_t optSeqNum
        const uint8_t* pData
        size_t lenData
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The length of the data to send.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optSeqNum</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Sequence number of first byte.<br />
</p>
<p>optSeqNum will be ignored if its value is<br />
WINC_CMDSOCKWR_SEQ_NUM_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pData</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>The data to send.<br />
</p>
<p>Maximum length of string is 1460<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenData</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pData.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKWRTO

##### Description

This function is used to send data to an arbitrary destination using the connectionless UDP protocol.

    bool WINC_CmdSOCKWRTO
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        WINC_TYPE typeRmtAddr
        uintptr_t rmtAddr
        size_t lenRmtAddr
        uint16_t rmtPort
        uint16_t length
        int32_t optSeqNum
        const uint8_t* pData
        size_t lenData
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeRmtAddr</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of rmtAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>rmtAddr</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>The address of the remote device.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenRmtAddr</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of rmtAddr.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>rmtPort</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The port number on the remote device.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The length of the data to send.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optSeqNum</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Sequence number of first byte.<br />
</p>
<p>optSeqNum will be ignored if its value is<br />
WINC_CMDSOCKWRTO_SEQ_NUM_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pData</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>The data to send.<br />
</p>
<p>Maximum length of string is 1472<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenData</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pData.<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_SOCKET_SOCKRD"></a>
#### WINC_CmdSOCKRD

##### Description

This function is used to read data from a socket.

Two AECs present notification of data received by the DCE:

- [WINC_AEC_ID_SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) indicates UDP data has been received.

- [WINC_AEC_ID_SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) indicates TCP data has been received.

The DTE is responsible for retrieving the datagram/stream data via the [WINC_CmdSOCKRD](#AN_FUNC_AT_SOCKET_SOCKRD) function.

For TCP sockets the DCE will indicate, via [WINC_AEC_ID_SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT), the number of bytes of data which are currently available for reading via the [WINC_CmdSOCKRD](#AN_FUNC_AT_SOCKET_SOCKRD) function. The DCE may issue multiple [WINC_AEC_ID_SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) AECs as data is received. When requesting data via the [WINC_CmdSOCKRD](#AN_FUNC_AT_SOCKET_SOCKRD) function the DTE may receive less data than request, the number of bytes provided by the DCE will be declared in the [WINC_CmdSOCKRD](#AN_FUNC_AT_SOCKET_SOCKRD) response before the data is presented. The DTE may request less data than that declared by the [WINC_AEC_ID_SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) AEC as being available, the remaining data will be available for subsequent reading.

For UDP sockets the DCE will indicate, via [WINC_AEC_ID_SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU), the number of bytes of data which were received in the oldest datagram received by the DCE. Only a single [WINC_AEC_ID_SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) will be issued by the DCE even if subsequent UDP datagrams are received. Reading data from the UDP socket via the [WINC_CmdSOCKRD](#AN_FUNC_AT_SOCKET_SOCKRD) function will read and discard the current datagram, if less data is requested than was indicated by the [WINC_AEC_ID_SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AEC the remaining unread data in the datagram will be discarded.

    bool WINC_CmdSOCKRD
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        uint8_t outputMode
        int32_t length
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>outputMode</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>The format the DTE wishes to receive the data.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ASCII</p></td>
<td style="text-align: left;"><p>ASCII or hex string.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>BINARY</p></td>
<td style="text-align: left;"><p>Binary.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>ASCII_EXT</p></td>
<td style="text-align: left;"><p>ASCII or hex string with extended information.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>The number of bytes the DTE wishes to read.<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<SOCK_ID\>,\<LENGTH\>,\<DATA\> | Socket read response |
| \<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<DATA\> | Socket read response (TCP extended) |
| \<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<PEND_DATAGRAM\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<DATA\> | Socket read response (UDP extended) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATAGRAM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending datagrams<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
IP_ADDRESS<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKRDBUF

##### Description

This function is used to read data from a socket buffer (UDP only).

    bool WINC_CmdSOCKRDBUF
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
        uint8_t outputMode
        int32_t length
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>outputMode</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>The format the DTE wishes to receive the data.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ASCII</p></td>
<td style="text-align: left;"><p>ASCII or hex string.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>BINARY</p></td>
<td style="text-align: left;"><p>Binary.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>ASCII_EXT</p></td>
<td style="text-align: left;"><p>ASCII or hex string with extended information.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>The number of bytes the DTE wishes to read.<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<SOCK_ID\>,\<LENGTH\>,\<DATA\> | Socket read response |
| \<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<DATA\> | Socket read response (TCP extended) |
| \<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<PEND_DATAGRAM\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<DATA\> | Socket read response (UDP extended) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATAGRAM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending datagrams<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
IP_ADDRESS<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKCL

##### Description

This function is used to close a socket.

    bool WINC_CmdSOCKCL
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t sockId
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p></td>
</tr>
</tbody>
</table>

| Response    | Description           |
|-------------|-----------------------|
| \<SOCK_ID\> | Socket close response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKLST

##### Description

This function is used to present a list of the WINC’s open sockets/connections.

    bool WINC_CmdSOCKLST
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t optSockId
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optSockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p>
<p>optSockId will be ignored if its value is<br />
WINC_CMDSOCKLST_SOCK_ID_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<SOCK_ID\>,\<PROTOCOL\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<LCL_PORT\> | Socket list response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The protocol in use<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UDP</p></td>
<td style="text-align: left;"><p>UDP.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>TCP</p></td>
<td style="text-align: left;"><p>TCP.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
IP_ADDRESS<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LCL_PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Local port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdSOCKC

##### Description

This function is used to read or set the socket configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdSOCKC
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t optSockId
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optSockId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The socket ID.<br />
</p>
<p>optSockId will be ignored if its value is<br />
WINC_CMDSOCKC_SOCK_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDSOCKC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_SOCKET_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SO_LINGER</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Socket linger enable/disable (TCP)<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLE</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLE</p></td>
<td style="text-align: left;"><p>Enable.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>SO_NODELAY</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Socket no delay (TCP)<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLE</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLE</p></td>
<td style="text-align: left;"><p>Enable.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>SO_KEEPALIVE</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Socket keep alive timeout (TCP)<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>SO_RCVBUF</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Socket receive buffer size (TCP)<br />
<br />
Valid range is 1460 to 32768<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>SO_SNDBUF</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Socket transmit buffer size (TCP)<br />
<br />
Valid range is 1460 to 32768<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>32</p></td>
<td style="text-align: left;"><p>IP_TOS</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Socket Type of Service (TCP/UDP)<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0x00</p></td>
<td style="text-align: left;"><p>NORM</p></td>
<td style="text-align: left;"><p>Normal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x04</p></td>
<td style="text-align: left;"><p>REL</p></td>
<td style="text-align: left;"><p>Reliability.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x08</p></td>
<td style="text-align: left;"><p>THRPUT</p></td>
<td style="text-align: left;"><p>Throughput.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x10</p></td>
<td style="text-align: left;"><p>LOW_DELAY</p></td>
<td style="text-align: left;"><p>Low delay.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>100</p></td>
<td style="text-align: left;"><p>ASYNC_NEXT_SN</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Async next sequence number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>101</p></td>
<td style="text-align: left;"><p>ASYNC_WIN_SZ</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Async window size<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>102</p></td>
<td style="text-align: left;"><p>ASYNC_MAX_FRM_SZ</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Async maximum frame size<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_SOCKIND

##### Description

**Socket established.**

| AEC | Description |
|----|----|
| \<SOCK_ID\>,\<LCL_ADDR\>,\<LCL_PORT\>,\<RMT_ADDR\>,\<RMT_PORT\> | TCP connection established |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LCL_ADDR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
IP_ADDRESS<br />
</p></td>
<td style="text-align: left;"><p>Local address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LCL_PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Local port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
IP_ADDRESS<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_SOCKET_SOCKRXT"></a>
#### WINC_AEC_ID_SOCKRXT

##### Description

**TCP receive.**

| AEC                                         | Description                  |
|---------------------------------------------|------------------------------|
| \<SOCK_ID\>,\<PEND_DATA\>                   | TCP receive (polled)         |
| \<SOCK_ID\>,\<LENGTH\>,\<DATA\>             | TCP receive (async)          |
| \<SOCK_ID\>,\<LENGTH\>,\<SEQ_NUM\>,\<DATA\> | TCP receive (async reliable) |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEQ_NUM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Sequence number of first byte<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_SOCKET_SOCKRXU"></a>
#### WINC_AEC_ID_SOCKRXU

##### Description

**UDP receive.**

| AEC | Description |
|----|----|
| \<SOCK_ID\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<PEND_DATA\>,\<PEND_DATAGRAM\> | UDP receive (polled) |
| \<SOCK_ID\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<LENGTH\>,\<DATA\> | UDP receive (async) |
| \<SOCK_ID\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<LENGTH\>,\<SEQ_NUM\>,\<DATA\> | UDP receive (async reliable) |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
IP_ADDRESS<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATAGRAM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending datagrams<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEQ_NUM&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Sequence number of first byte<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SOCKCL

##### Description

**Socket close.**

| AEC         | Description           |
|-------------|-----------------------|
| \<SOCK_ID\> | Socket close response |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SOCKTLS

##### Description

**TLS success.**

| AEC         | Description |
|-------------|-------------|
| \<SOCK_ID\> | TLS succeed |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SOCKERR

##### Description

**Socket error.**

| AEC                        | Description     |
|----------------------------|-----------------|
| \<SOCK_ID\>,\<ERROR_CODE\> | TCP bind failed |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_SOCKO_1"></a>
**Opening a TCP server socket**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Open a TCP socket
    APP->>API: WINC_CmdSOCKO(2)
    Note left of API: Socket ID 5 created
    API->>APP: Response:WINC_CMD_ID_SOCKO(5)
    API->>APP: Status:WINC_CMD_ID_SOCKO(OK)
    Note right of APP: Bind socket to local port 5678
    APP->>API: WINC_CmdSOCKBL(5,5678)
    API->>APP: Status:WINC_CMD_ID_SOCKBL(OK)
    Note left of API: New socket connection on port 5678
    API->>APP: AEC:WINC_AEC_ID_SOCKIND(6,"1.2.3.4",5678,"11.22.33.44",12345)
```

<a id="EXAMPLE_SOCKRD_1"></a>
**Basic socket read**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note left of API: Indicates 15 bytes are present
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,15)
    Note right of APP: Read 10 bytes in ASCII mode
    APP->>API: WINC_CmdSOCKRD(6,1,10)
    Note left of API: 10 bytes returned
    API->>APP: Response:WINC_CMD_ID_SOCKRD(6,10,"1234567890")
    API->>APP: Status:WINC_CMD_ID_SOCKRD(OK)
    Note left of API: An additional 2 bytes have been received
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,7)
```

<a id="EXAMPLE_SOCKRD_2"></a>
**In-band socket read**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note left of API: Indicates 20 bytes have been received
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,20)
    Note right of APP: Read 10 bytes in ASCII mode with extended information
    APP->>API: WINC_CmdSOCKRD(6,3,10)
    Note left of API: 10 bytes returned, indicates 10 bytes remain
    API->>APP: Response:WINC_CMD_ID_SOCKRD(6,10,10,"1234567890")
    API->>APP: Status:WINC_CMD_ID_SOCKRD(OK)
    Note right of APP: Read 4 bytes in ASCII mode with extended information
    APP->>API: WINC_CmdSOCKRD(6,3,4)
    Note left of API: 4 bytes returned, indicates 6 bytes remain
    API->>APP: Response:WINC_CMD_ID_SOCKRD(6,4,6,"abcd")
    API->>APP: Status:WINC_CMD_ID_SOCKRD(OK)
```

<a id="EXAMPLE_SOCKRXT_1"></a>
**Simple asynchronous socket read**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Configure socket ASYNC_MAX_FRM_SZ to be 1500 bytes
    APP->>API: WINC_CmdSOCKC(6,102,1500)
    API->>APP: Status:WINC_CMD_ID_SOCKC(OK)
    Note left of API: 10 bytes received
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,10,"1234567890")
    Note left of API: 4 bytes received
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,4,"abcd")
```

<a id="EXAMPLE_SOCKRXT_2"></a>
**Reliable asynchronous socket read**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Configure socket ASYNC_MAX_FRM_SZ to be 1500 bytes
    APP->>API: WINC_CmdSOCKC(6,102,1500)
    API->>APP: Status:WINC_CMD_ID_SOCKC(OK)
    Note right of APP: Configure socket ASYNC_WIN_SZ to be 8 bytes
    APP->>API: WINC_CmdSOCKC(6,101,8)
    API->>APP: Status:WINC_CMD_ID_SOCKC(OK)
    Note left of API: 8 bytes received, sequence number 0 to 7
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,8,0,"12345678")
    Note right of APP: Configure ASYNC_NEXT_SN to be 8
    APP->>API: WINC_CmdSOCKC(6,100,8)
    API->>APP: Status:WINC_CMD_ID_SOCKC(OK)
    Note left of API: 8 bytes received, sequence number 8 to 15
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,8,8,"90abcdef")
    Note right of APP: Configure ASYNC_NEXT_SN to be 12
    APP->>API: WINC_CmdSOCKC(6,100,12)
    API->>APP: Status:WINC_CMD_ID_SOCKC(OK)
    Note left of API: 4 bytes received, sequence number 16 to 19
    API->>APP: AEC:WINC_AEC_ID_SOCKRXT(6,4,16,"ghij")
```

<a id="EXAMPLE_SOCKTLSCLI"></a>
**Set TLS configuration 1 for TLS client**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Enable server domain verification
    APP->>API: WINC_CmdTLSC(1,41,1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify server domain name
    APP->>API: WINC_CmdTLSC(1,6,"ServerDomain")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Enable server authentication
    APP->>API: WINC_CmdTLSC(1,40,1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of CA certificate
    APP->>API: WINC_CmdTLSC(1,1,"ServerRootCACert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of client certificate (required if server authenticates the client)
    APP->>API: WINC_CmdTLSC(1,2,"MyClientCert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of client private key (required if server authenticates the client)
    APP->>API: WINC_CmdTLSC(1,3,"MyClientPrivateKey")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
```

<a id="EXAMPLE_12de0326b22680d3b9cc3d612dba34e5f4d023fe"></a>
**Open a TLS client socket with AT+SOCK**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Open a TCP socket
    APP->>API: WINC_CmdSOCKO(2)
    API->>APP: Status:WINC_CMD_ID_SOCKO(OK)
    Note left of API: Socket created
    API->>APP: AEC:WINC_AEC_ID_SOCKO(17603)
    Note right of APP: Upgrade socket to TLS, using configuration 1
    APP->>API: WINC_CmdSOCKTLS(17603,1)
    API->>APP: Status:WINC_CMD_ID_SOCKTLS(OK)
    Note right of APP: Bind socket to server
    APP->>API: WINC_CmdSOCKBR(17603,"example.com",443)
    API->>APP: Status:WINC_CMD_ID_SOCKBR(OK)
    Note left of API: Socket connected
    API->>APP: AEC:WINC_AEC_ID_SOCKIND(17603,"1.2.3.4",65333,"5.6.7.8",443)
    Note left of API: Socket upgraded to TLS
    API->>APP: AEC:WINC_AEC_ID_SOCKTLS(17603)
```

<a id="EXAMPLE_SOCKTLSSRV"></a>
**Set TLS configuration 2 for TLS server**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify file name of server certificate
    APP->>API: WINC_CmdTLSC(2,2,"MyServerCertChain")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of server private key
    APP->>API: WINC_CmdTLSC(2,3,"MyServerPrivateKey")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of server DH parameters (DHE cipher suite only)
    APP->>API: WINC_CmdTLSC(2,8,"MyDhParams")
    API->>APP: Status:WINC_CMD_ID_TLSC(0K)
    Note right of APP: Disable client authentication
    APP->>API: WINC_CmdTLSC(2,40,0)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Disable client domain name verification
    APP->>API: WINC_CmdTLSC(2,41,0)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
```

<a id="EXAMPLE_a70e12e9f2deb08dda4c674bca8584fd9c59e257"></a>
**Open a TLS server socket with AT+SOCK**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Open a TCP socket
    APP->>API: WINC_CmdSOCKO(2)
    API->>APP: Status:WINC_CMD_ID_SOCKO(OK)
    Note left of API: Socket created
    API->>APP: AEC:WINC_AEC_ID_SOCKO(16037)
    Note right of APP: Upgrade socket to TLS, using configuration 2
    APP->>API: WINC_CmdSOCKTLS(16037,2)
    API->>APP: Status:WINC_CMD_ID_SOCKTLS(OK)
    Note right of APP: Bind socket to local port 443
    APP->>API: WINC_CmdSOCKBL(16037,443)
    API->>APP: Status:WINC_CMD_ID_SOCKBL(OK)
    Note left of API: New socket connection on port 443
    API->>APP: AEC:WINC_AEC_ID_SOCKIND(16037,"1.2.3.4",443,"11.22.33.44",12345)
    Note left of API: Socket upgraded to TLS
    API->>APP: AEC:WINC_AEC_ID_SOCKTLS(16037)
```

<a id="EXAMPLE_SOCKRDBUF"></a>
**Reading partial datagram**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Open a UDP socket
    APP->>API: WINC_CmdSOCKO(1)
    Note left of API: Socket ID 7 created
    API->>APP: Response:WINC_CMD_ID_SOCKO(7)
    API->>APP: Status:WINC_CMD_ID_SOCKO(OK)
    Note right of APP: Bind socket to port 1234
    APP->>API: WINC_CmdSOCKBL(7,1234)
    API->>APP: Status:WINC_CMD_ID_SOCKBL(OK)
    Note left of API: 100 bytes datagram received
    API->>APP: AEC:WINC_AEC_ID_SOCKRXU(7,"1.2.3.4",1234,100,1)
    Note right of APP: Read first 10 bytes of datagram
    APP->>API: WINC_CmdSOCKRDBUF(7,1,10)
    API->>APP: Response:WINC_CMD_ID_SOCKRDBUF(=7,10,[11223344556677889900])
    Note right of APP: Read second 10 bytes of datagram
    APP->>API: WINC_CmdSOCKRDBUF(7,1,10)
    API->>APP: Response:WINC_CMD_ID_SOCKRDBUF(=7,10,[AABBCCDDEEFF11223344])
    API->>APP: Status:WINC_CMD_ID_SOCKRDBUF(OK)
    Note right of APP: Read first 10 bytes of next datagram and discard remaining (and buffered)
    APP->>API: WINC_CmdSOCKRD(7,1,10)
    API->>APP: Response:WINC_CMD_ID_SOCKRDBUF(=7,10,[1234567890ABCDEF0011])
    API->>APP: Status:WINC_CMD_ID_SOCKRD(OK)
```

---
<a id="AN_MOD_TIME"></a>
## TIME (Module ID = 16)

### Function Reference:

#### WINC_CmdTIME

##### Description

This function is used to set or query the system time.

Three formats of time are supported, two are in UTC seconds and one is a string based on RFC3339 / ISO-8601 format:

1.  UNIX timestamp - UTC seconds since 1st January 1970

2.  NTP time - UTC seconds since 1st January 1900

3.  RFC3339 / ISO-8601 - String representation of date/time

RFC3338 / ISO-8601 format represents the time as:

    YYYY-MM-DDTHH:MM:SS.ssZ

For example:

    2019-02-28T12:34:56.01Z - 28th February 2019, 12:34 PM 56.01 seconds (UTC+0)

    bool WINC_CmdTIME
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t optFormat
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optFormat</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Format of time.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UTC_UNIX</p></td>
<td style="text-align: left;"><p>UTC seconds (epoch 01/01/1970 - UNIX timestamp).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>UTC_NTP</p></td>
<td style="text-align: left;"><p>UTC seconds (epoch 01/01/1900 - NTP time).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>RFC3339</p></td>
<td style="text-align: left;"><p>RFC3339 / ISO-8601 format.</p></td>
</tr>
</tbody>
</table>
<p>optFormat will be ignored if its value is<br />
WINC_CMDTIME_FORMAT_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdTIMEUTCSEC

##### Description

This function is used to set or query the system time.

    bool WINC_CmdTIMEUTCSEC
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t format
        uint32_t utcSec
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>format</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Format of time.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UTC_UNIX</p></td>
<td style="text-align: left;"><p>UTC seconds (epoch 01/01/1970 - UNIX timestamp).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>UTC_NTP</p></td>
<td style="text-align: left;"><p>UTC seconds (epoch 01/01/1900 - NTP time).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>RFC3339</p></td>
<td style="text-align: left;"><p>RFC3339 / ISO-8601 format.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>utcSec</p></td>
<td style="text-align: left;"><p>uint32_t</p></td>
<td style="text-align: left;"><p>UTC seconds.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdTIMERFC

##### Description

This function is used to set or query the system time.

    bool WINC_CmdTIMERFC
    (
        WINC_CMD_REQ_HANDLE handle
        const uint8_t* pDateTime
        size_t lenDateTime
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pDateTime</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Date/time in format YYYY-MM-DDTHH:MM:SS.00Z.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenDateTime</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pDateTime.<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_TIME

##### Description

**Time report.**

| AEC      | Description |
|----------|-------------|
| \<TIME\> | Time report |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TIME&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Current time<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_TLS"></a>
## TLS (Module ID = 17)

### Introduction

Transport Layer Security (TLS) establishes an encrypted communication channel between a client and server, ensuring confidentiality and integrity of exchanged data.

The WINCS02 can establish a TLS session in either client mode or server mode. The TLS configuration parameters described in this module are used in conjunction with the [SOCK](#AN_MOD_SOCKET), [MQTT](#AN_MOD_MQTT), and [WSTA](#AN_MOD_WSTA) modules to enable secure connections.

#### TLS configuration

Set TLS parameters using the [WINC_CmdTLSC](#AN_FUNC_AT_TLS_TLSC) and [WINC_CmdTLSCSC](#AN_FUNC_AT_TLS_TLSCSC) functions.

See examples [Basic TLS client configuration](#EXAMPLE_SOCKTLSCLI) and [Basic TLS server configuration](#EXAMPLE_SOCKTLSSRV).

##### Certificate and Private Key

The X.509 certificate and the corresponding private key are required for the peer to authenticate the DCE.

The certificate file name can be specified via [CERT_NAME](#AN_FUNC_TLSC_STORE_ID_CERT_NAME) and must be in PEM or DER format. If the file contains multiple certificates, it must be in PEM format. The private key file name can be specified via [PRI_KEY_NAME](#AN_FUNC_TLSC_STORE_ID_PRI_KEY_NAME) and must be in PEM or DER format. If the private key is encrypted, the password must also be provided via [PRI_KEY_PASSWORD](#AN_FUNC_TLSC_STORE_ID_PRI_KEY_PASSWORD).

Certificate and private key are always required for TLS server mode. For client mode, they are required if the server authenticates the client.

##### Server Name

The TLS Server Name Indication (SNI) extension allows a client to specify the hostname it is connecting to during the TLS handshake. This enables a server hosting multiple domains on the same IP address to present the correct certificate.

The server name is configured via [SERVER_NAME](#AN_FUNC_TLSC_STORE_ID_SERVER_NAME). This parameter only applies to client mode.

##### Peer authentication

Peer authentication validates the peer’s certificate chain against trusted CA certificates provided in the CA certificate file.

When peer authentication is enabled via [PEER_AUTH](#AN_FUNC_TLSC_STORE_ID_PEER_AUTH), a valid CA certificate file name must be provided via [CA_CERT_NAME](#AN_FUNC_TLSC_STORE_ID_CA_CERT_NAME). If the file contains multiple certificates, it must be in PEM format.

Peer authentication is recommended in client mode.

##### Domain Name Verification

Domain name verification confirms the peer’s certificate was issued for the expected server by matching the configured domain name against the certificate’s Subject Alternative Name (SAN), or Common Name (CN) if no SAN is present.

When domain name verification is enabled via [PEER_DOMAIN_VERIFY](#AN_FUNC_TLSC_STORE_ID_PEER_DOMAIN_VERIFY), the expected domain name must be provided via [DOMAIN_NAME](#AN_FUNC_TLSC_STORE_ID_DOMAIN_NAME).

Peer domain verification is recommented in client mode.

##### Cipher Suites

A cipher suite defines the algorithms used for key exchange, data encryption, and message authentication during a TLS session. The cipher suites index ([CIPHER_SUITES_IDX](#AN_FUNC_TLSC_STORE_ID_CIPHER_SUITES_IDX)) references a cipher suite list configured using the [WINC_CmdTLSCSC](#AN_FUNC_AT_TLS_TLSCSC) function.

##### Diffie-Hellman Parameters

Diffie-Hellman (DH) parameters define the prime number and generator used to establish a shared secret between client and server without transmitting the secret itself. The file containing the Diffie-Hellman parameters must be specified via [DH_PARAM_NAME](#AN_FUNC_TLSC_STORE_ID_DH_PARAM_NAME) if DHE key exchange cipher suites are enabled. Diffie-Hellman parameters are only required for server mode.

##### Certificate Pinning

Certificate pinning allows specifying a list of expected hash digest/hash algorithm pairs. During the TLS handshake, the peer’s leaf certificate is hashed and compared against the configured digests. If none match, the connection is rejected.

Certificate pinning provides additional security beyond CA-based authentication by ensuring connections are only made to servers with specific known certificates, protecting against compromised CAs or misissued certificates.

See example [configuring certificate digests](#EXAMPLE_TLS_DIGEST)

##### External crypto operations

TLS client authentication allows a server to verify the client’s identity by requesting the client to sign a message with its private key, which is verified against the public key in the X.509 certificate. Signing operations can be delegated to an external crypto device via the [EXTCRYPTO](#AN_MOD_EXTCRYPTO) module.

When signing is enabled via [EXTCRYPTO_OPS](#AN_FUNC_TLSC_STORE_ID_EXTCRYPTO_OPS), only the certificate file must be provided via [CERT_NAME](#AN_FUNC_TLSC_STORE_ID_CERT_NAME). The private key is not required as it resides in the external crypto device.

See example [TLS client configuration with external crypto device](#EXAMPLE_EXTCRYPTO_TLS)

##### Server Renegotiation Extension

The TLS renegotiation info extension was introduced to address the TLS renegotiation vulnerability (CVE-2009-3555). Servers that are patched against this vulnerability include the renegotiation info extension during the TLS handshake.

When the server renegotiation info ([SERVER_RENEG_INFO](#AN_FUNC_TLSC_STORE_ID_SERVER_RENEG_INFO)) is configured as "required", the client rejects connections to servers that do not provide it. Othwerise, the client will connect even if the server does not send the extension. "required" is the recommented setting unless connecting to legacy servers that do not support the security patch. This option is only applicable to client mode.

##### Session Caching

Session caching enables TLS session resumption using cached session data. When a TLS handshake completes, both client and server retain session state (including the master secret and negotiated cipher suite). On subsequent connections to the same server, this cached session can be reused to perform an abbreviated handshake that skips computationally expensive public-key operations. Session caching significantly reduces connection establishment time.

When a TLS configuration parameter is modified, the previously cached session is discarded.

---
#### TLS Cipher Suite codes

**The supported cipher suites are listed below.**

<table>
<tbody>
<tr>
<td>Code</td>
<td>Cipher Suite Name</td>
</tr>
<tr>
<td>0x002F</td>
<td>TLS_RSA_WITH_AES_128_CBC_SHA</td>
</tr>
<tr>
<td>0x0035</td>
<td>TLS_RSA_WITH_AES_256_CBC_SHA</td>
</tr>
<tr>
<td>0x0033</td>
<td>TLS_DHE_RSA_WITH_AES_128_CBC_SHA</td>
</tr>
<tr>
<td>0x0039</td>
<td>TLS_DHE_RSA_WITH_AES_256_CBC_SHA</td>
</tr>
<tr>
<td>0x003C</td>
<td>TLS_RSA_WITH_AES_128_CBC_SHA256</td>
</tr>
<tr>
<td>0x003D</td>
<td>TLS_RSA_WITH_AES_256_CBC_SHA256</td>
</tr>
<tr>
<td>0x0067</td>
<td>TLS_DHE_RSA_WITH_AES_128_CBC_SHA256</td>
</tr>
<tr>
<td>0x006B</td>
<td>TLS_DHE_RSA_WITH_AES_256_CBC_SHA256</td>
</tr>
<tr>
<td>0x009C</td>
<td>TLS_RSA_WITH_AES_128_GCM_SHA256</td>
</tr>
<tr>
<td>0x009D</td>
<td>TLS_RSA_WITH_AES_256_GCM_SHA384</td>
</tr>
<tr>
<td>0x009E</td>
<td>TLS_DHE_RSA_WITH_AES_128_GCM_SHA256</td>
</tr>
<tr>
<td>0x009F</td>
<td>TLS_DHE_RSA_WITH_AES_256_GCM_SHA384</td>
</tr>
<tr>
<td>0xC009</td>
<td>TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA</td>
</tr>
<tr>
<td>0xC00A</td>
<td>TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA</td>
</tr>
<tr>
<td>0xC013</td>
<td>TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA</td>
</tr>
<tr>
<td>0xC014</td>
<td>TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA</td>
</tr>
<tr>
<td>0xC023</td>
<td>TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256</td>
</tr>
<tr>
<td>0xC024</td>
<td>TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384</td>
</tr>
<tr>
<td>0xC027</td>
<td>TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256</td>
</tr>
<tr>
<td>0xC028</td>
<td>TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384</td>
</tr>
<tr>
<td>0xC02B</td>
<td>TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256</td>
</tr>
<tr>
<td>0xC02C</td>
<td>TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384</td>
</tr>
<tr>
<td>0xC02F</td>
<td>TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256</td>
</tr>
<tr>
<td>0xC030</td>
<td>TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384</td>
</tr>
</tbody>
</table>

---
### TLS Error Codes

To assist with debugging TLS issues, error codes from wolfSSL can be obtained by enabling logging via [WINC_CmdSYSLOGC](#AN_FUNC_AT_SYSLOG_SYSLOGC).

<table>
<tbody>
<tr>
<td>Error Code Enum</td>
<td>Error Code</td>
<td>Error Description</td>
</tr>
<tr>
<td>OPEN_RAN_E</td>
<td>-101</td>
<td>opening random device error</td>
</tr>
<tr>
<td>READ_RAN_E</td>
<td>-102</td>
<td>reading random device error</td>
</tr>
<tr>
<td>WINCRYPT_E</td>
<td>-103</td>
<td>windows crypt init error</td>
</tr>
<tr>
<td>CRYPTGEN_E</td>
<td>-104</td>
<td>windows crypt generation error</td>
</tr>
<tr>
<td>RAN_BLOCK_E</td>
<td>-105</td>
<td>reading random device would block</td>
</tr>
<tr>
<td>BAD_MUTEX_E</td>
<td>-106</td>
<td>Bad mutex operation</td>
</tr>
<tr>
<td>MP_INIT_E</td>
<td>-110</td>
<td>mp_init error state</td>
</tr>
<tr>
<td>MP_READ_E</td>
<td>-111</td>
<td>mp_read error state</td>
</tr>
<tr>
<td>MP_EXPTMOD_E</td>
<td>-112</td>
<td>mp_exptmod error state</td>
</tr>
<tr>
<td>MP_TO_E</td>
<td>-113</td>
<td>mp_to_xxx error state, can’t convert</td>
</tr>
<tr>
<td>MP_SUB_E</td>
<td>-114</td>
<td>mp_sub error state, can’t subtract</td>
</tr>
<tr>
<td>MP_ADD_E</td>
<td>-115</td>
<td>mp_add error state, can’t add</td>
</tr>
<tr>
<td>MP_MUL_E</td>
<td>-116</td>
<td>mp_mul error state, can’t multiply</td>
</tr>
<tr>
<td>MP_MULMOD_E</td>
<td>-117</td>
<td>mp_mulmod error state, can’t multiply mod</td>
</tr>
<tr>
<td>MP_MOD_E</td>
<td>-118</td>
<td>mp_mod error state, can’t mod</td>
</tr>
<tr>
<td>MP_INVMOD_E</td>
<td>-119</td>
<td>mp_invmod error state, can’t inv mod</td>
</tr>
<tr>
<td>MP_CMP_E</td>
<td>-120</td>
<td>mp_cmp error state</td>
</tr>
<tr>
<td>MP_ZERO_E</td>
<td>-121</td>
<td>got a mp zero result, not expected</td>
</tr>
<tr>
<td>MEMORY_E</td>
<td>-125</td>
<td>out of memory error</td>
</tr>
<tr>
<td>RSA_WRONG_TYPE_E</td>
<td>-130</td>
<td>RSA wrong block type for RSA function</td>
</tr>
<tr>
<td>RSA_BUFFER_E</td>
<td>-131</td>
<td>RSA buffer error, output too small or input too large</td>
</tr>
<tr>
<td>BUFFER_E</td>
<td>-132</td>
<td>output buffer too small or input too large</td>
</tr>
<tr>
<td>ALGO_ID_E</td>
<td>-133</td>
<td>setting algo id error</td>
</tr>
<tr>
<td>PUBLIC_KEY_E</td>
<td>-134</td>
<td>setting public key error</td>
</tr>
<tr>
<td>DATE_E</td>
<td>-135</td>
<td>setting date validity error</td>
</tr>
<tr>
<td>SUBJECT_E</td>
<td>-136</td>
<td>setting subject name error</td>
</tr>
<tr>
<td>ISSUER_E</td>
<td>-137</td>
<td>setting issuer name error</td>
</tr>
<tr>
<td>CA_TRUE_E</td>
<td>-138</td>
<td>setting CA basic constraint true error</td>
</tr>
<tr>
<td>EXTENSIONS_E</td>
<td>-139</td>
<td>setting extensions error</td>
</tr>
<tr>
<td>ASN_PARSE_E</td>
<td>-140</td>
<td>ASN parsing error, invalid input</td>
</tr>
<tr>
<td>ASN_VERSION_E</td>
<td>-141</td>
<td>ASN version error, invalid number</td>
</tr>
<tr>
<td>ASN_GETINT_E</td>
<td>-142</td>
<td>ASN get big int error, invalid data</td>
</tr>
<tr>
<td>ASN_RSA_KEY_E</td>
<td>-143</td>
<td>ASN key init error, invalid input</td>
</tr>
<tr>
<td>ASN_OBJECT_ID_E</td>
<td>-144</td>
<td>ASN object id error, invalid id</td>
</tr>
<tr>
<td>ASN_TAG_NULL_E</td>
<td>-145</td>
<td>ASN tag error, not null</td>
</tr>
<tr>
<td>ASN_EXPECT_0_E</td>
<td>-146</td>
<td>ASN expect error, not zero</td>
</tr>
<tr>
<td>ASN_BITSTR_E</td>
<td>-147</td>
<td>ASN bit string error, wrong id</td>
</tr>
<tr>
<td>ASN_UNKNOWN_OID_E</td>
<td>-148</td>
<td>ASN oid error, unknown sum id</td>
</tr>
<tr>
<td>ASN_DATE_SZ_E</td>
<td>-149</td>
<td>ASN date error, bad size</td>
</tr>
<tr>
<td>ASN_BEFORE_DATE_E</td>
<td>-150</td>
<td>ASN date error, current date before</td>
</tr>
<tr>
<td>ASN_AFTER_DATE_E</td>
<td>-151</td>
<td>ASN date error, current date after</td>
</tr>
<tr>
<td>ASN_SIG_OID_E</td>
<td>-152</td>
<td>ASN signature error, mismatched oid</td>
</tr>
<tr>
<td>ASN_TIME_E</td>
<td>-153</td>
<td>ASN time error, unknown time type</td>
</tr>
<tr>
<td>ASN_INPUT_E</td>
<td>-154</td>
<td>ASN input error, not enough data</td>
</tr>
<tr>
<td>ASN_SIG_CONFIRM_E</td>
<td>-155</td>
<td>ASN sig error, confirm failure</td>
</tr>
<tr>
<td>ASN_SIG_HASH_E</td>
<td>-156</td>
<td>ASN sig error, unsupported hash type</td>
</tr>
<tr>
<td>ASN_SIG_KEY_E</td>
<td>-157</td>
<td>ASN sig error, unsupported key type</td>
</tr>
<tr>
<td>ASN_DH_KEY_E</td>
<td>-158</td>
<td>ASN key init error, invalid input</td>
</tr>
<tr>
<td>ASN_CRIT_EXT_E</td>
<td>-160</td>
<td>ASN unsupported critical extension</td>
</tr>
<tr>
<td>ECC_BAD_ARG_E</td>
<td>-170</td>
<td>ECC input argument of wrong type</td>
</tr>
<tr>
<td>ASN_ECC_KEY_E</td>
<td>-171</td>
<td>ASN ECC bad input</td>
</tr>
<tr>
<td>ECC_CURVE_OID_E</td>
<td>-172</td>
<td>Unsupported ECC OID curve type</td>
</tr>
<tr>
<td>BAD_FUNC_ARG</td>
<td>-173</td>
<td>Bad function argument provided</td>
</tr>
<tr>
<td>NOT_COMPILED_IN</td>
<td>-174</td>
<td>Feature not compiled in</td>
</tr>
<tr>
<td>UNICODE_SIZE_E</td>
<td>-175</td>
<td>Unicode password too big</td>
</tr>
<tr>
<td>NO_PASSWORD</td>
<td>-176</td>
<td>no password provided by user</td>
</tr>
<tr>
<td>ALT_NAME_E</td>
<td>-177</td>
<td>alt name size problem, too big</td>
</tr>
<tr>
<td>AES_GCM_AUTH_E</td>
<td>-180</td>
<td>AES-GCM Authentication check failure</td>
</tr>
<tr>
<td>AES_CCM_AUTH_E</td>
<td>-181</td>
<td>AES-CCM Authentication check failure</td>
</tr>
<tr>
<td>CAVIUM_INIT_E</td>
<td>-182</td>
<td>Cavium Init type error</td>
</tr>
<tr>
<td>COMPRESS_INIT_E</td>
<td>-183</td>
<td>Compress init error</td>
</tr>
<tr>
<td>COMPRESS_E</td>
<td>-184</td>
<td>Compress error</td>
</tr>
<tr>
<td>DECOMPRESS_INIT_E</td>
<td>-185</td>
<td>DeCompress init error</td>
</tr>
<tr>
<td>DECOMPRESS_E</td>
<td>-186</td>
<td>DeCompress error</td>
</tr>
<tr>
<td>BAD_ALIGN_E</td>
<td>-187</td>
<td>Bad alignment for operation, no alloc</td>
</tr>
<tr>
<td>ASN_NO_SIGNER_E</td>
<td>-188</td>
<td>ASN sig error, no CA signer to verify certificate</td>
</tr>
<tr>
<td>ASN_CRL_CONFIRM_E</td>
<td>-189</td>
<td>ASN CRL no signer to confirm failure</td>
</tr>
<tr>
<td>ASN_CRL_NO_SIGNER_E</td>
<td>-190</td>
<td>ASN CRL no signer to confirm failure</td>
</tr>
<tr>
<td>ASN_OCSP_CONFIRM_E</td>
<td>-191</td>
<td>ASN OCSP signature confirm failure</td>
</tr>
<tr>
<td>BAD_ENC_STATE_E</td>
<td>-192</td>
<td>Bad ecc enc state operation</td>
</tr>
<tr>
<td>BAD_PADDING_E</td>
<td>-193</td>
<td>Bad padding, msg not correct length</td>
</tr>
<tr>
<td>REQ_ATTRIBUTE_E</td>
<td>-194</td>
<td>Setting cert request attributes error</td>
</tr>
<tr>
<td>PKCS7_OID_E</td>
<td>-195</td>
<td>PKCS#7, mismatched OID error</td>
</tr>
<tr>
<td>PKCS7_RECIP_E</td>
<td>-196</td>
<td>PKCS#7, recipient error</td>
</tr>
<tr>
<td>FIPS_NOT_ALLOWED_E</td>
<td>-197</td>
<td>FIPS not allowed error</td>
</tr>
<tr>
<td>ASN_NAME_INVALID_E</td>
<td>-198</td>
<td>ASN name constraint error</td>
</tr>
<tr>
<td>RNG_FAILURE_E</td>
<td>-199</td>
<td>RNG Failed, Reinitialize</td>
</tr>
<tr>
<td>HMAC_MIN_KEYLEN_E</td>
<td>-200</td>
<td>FIPS Mode HMAC Minimum Key Length error</td>
</tr>
<tr>
<td>RSA_PAD_E</td>
<td>-201</td>
<td>RSA Padding Error</td>
</tr>
<tr>
<td>LENGTH_ONLY_E</td>
<td>-202</td>
<td>Returning output length only</td>
</tr>
<tr>
<td>IN_CORE_FIPS_E</td>
<td>-203</td>
<td>In Core Integrity check failure</td>
</tr>
<tr>
<td>AES_KAT_FIPS_E</td>
<td>-204</td>
<td>AES KAT failure</td>
</tr>
<tr>
<td>DES3_KAT_FIPS_E</td>
<td>-205</td>
<td>DES3 KAT failure</td>
</tr>
<tr>
<td>HMAC_KAT_FIPS_E</td>
<td>-206</td>
<td>HMAC KAT failure</td>
</tr>
<tr>
<td>RSA_KAT_FIPS_E</td>
<td>-207</td>
<td>RSA KAT failure</td>
</tr>
<tr>
<td>DRBG_KAT_FIPS_E</td>
<td>-208</td>
<td>HASH DRBG KAT failure</td>
</tr>
<tr>
<td>DRBG_CONT_FIPS_E</td>
<td>-209</td>
<td>HASH DRBG Continuous test failure</td>
</tr>
<tr>
<td>AESGCM_KAT_FIPS_E</td>
<td>-210</td>
<td>AESGCM KAT failure</td>
</tr>
<tr>
<td>THREAD_STORE_KEY_E</td>
<td>-211</td>
<td>Thread local storage key create failure</td>
</tr>
<tr>
<td>THREAD_STORE_SET_E</td>
<td>-212</td>
<td>Thread local storage key set failure</td>
</tr>
<tr>
<td>MAC_CMP_FAILED_E</td>
<td>-213</td>
<td>MAC comparison failed</td>
</tr>
<tr>
<td>IS_POINT_E</td>
<td>-214</td>
<td>ECC is point on curve failed</td>
</tr>
<tr>
<td>ECC_INF_E</td>
<td>-215</td>
<td>ECC point infinity error</td>
</tr>
<tr>
<td>ECC_PRIV_KEY_E</td>
<td>-216</td>
<td>ECC private key not valid error</td>
</tr>
<tr>
<td>SRP_CALL_ORDER_E</td>
<td>-217</td>
<td>SRP function called in the wrong order</td>
</tr>
<tr>
<td>SRP_VERIFY_E</td>
<td>-218</td>
<td>SRP proof verification failed</td>
</tr>
<tr>
<td>SRP_BAD_KEY_E</td>
<td>-219</td>
<td>SRP bad ephemeral values</td>
</tr>
<tr>
<td>ASN_NO_SKID</td>
<td>-220</td>
<td>ASN no Subject Key Identifier found</td>
</tr>
<tr>
<td>ASN_NO_AKID</td>
<td>-221</td>
<td>ASN no Authority Key Identifier found</td>
</tr>
<tr>
<td>ASN_NO_KEYUSAGE</td>
<td>-223</td>
<td>ASN no Key Usage found</td>
</tr>
<tr>
<td>SKID_E</td>
<td>-224</td>
<td>Setting Subject Key Identifier error</td>
</tr>
<tr>
<td>AKID_E</td>
<td>-225</td>
<td>Setting Authority Key Identifier error</td>
</tr>
<tr>
<td>KEYUSAGE_E</td>
<td>-226</td>
<td>Bad Key Usage value</td>
</tr>
<tr>
<td>CERTPOLICIES_E</td>
<td>-227</td>
<td>Setting Certificate Policies error</td>
</tr>
<tr>
<td>WC_INIT_E</td>
<td>-228</td>
<td>wolfCrypt failed to initialize</td>
</tr>
<tr>
<td>SIG_VERIFY_E</td>
<td>-229</td>
<td>wolfCrypt signature verify error</td>
</tr>
<tr>
<td>BAD_PKCS7_SIGNEEDS_CHECKCOND_E</td>
<td>-230</td>
<td>Bad condition variable operation</td>
</tr>
<tr>
<td>SIG_TYPE_E</td>
<td>-231</td>
<td>Signature Type not enabled/available</td>
</tr>
<tr>
<td>HASH_TYPE_E</td>
<td>-232</td>
<td>Hash Type not enabled/available</td>
</tr>
<tr>
<td>WC_KEY_SIZE_E</td>
<td>-234</td>
<td>Key size error, either too small or large</td>
</tr>
<tr>
<td>ASN_COUNTRY_SIZE_E</td>
<td>-235</td>
<td>ASN Cert Gen, invalid country code size</td>
</tr>
<tr>
<td>MISSING_RNG_E</td>
<td>-236</td>
<td>RNG required but not provided</td>
</tr>
<tr>
<td>ASN_PATHLEN_SIZE_E</td>
<td>-237</td>
<td>ASN CA path length too large error</td>
</tr>
<tr>
<td>ASN_PATHLEN_INV_E</td>
<td>-238</td>
<td>ASN CA path length inversion error</td>
</tr>
<tr>
<td>BAD_KEYWRAP_ALG_E</td>
<td>-239</td>
<td>Algorithm error with keywrap</td>
</tr>
<tr>
<td>BAD_KEYWRAP_IV_E</td>
<td>-240</td>
<td>Decrypted AES key wrap IV incorrect</td>
</tr>
<tr>
<td>WC_CLEANUP_E</td>
<td>-241</td>
<td>wolfCrypt cleanup failed</td>
</tr>
<tr>
<td>ECC_CDH_KAT_FIPS_E</td>
<td>-242</td>
<td>ECC CDH known answer test failure</td>
</tr>
<tr>
<td>DH_CHECK_PUB_E</td>
<td>-243</td>
<td>DH check public key error</td>
</tr>
<tr>
<td>BAD_PATH_ERROR</td>
<td>-244</td>
<td>Bad path for opendir</td>
</tr>
<tr>
<td>ASYNC_OP_E</td>
<td>-245</td>
<td>Async operation error</td>
</tr>
<tr>
<td>ECC_PRIVATEONLY_E</td>
<td>-246</td>
<td>Invalid use of private only ECC key</td>
</tr>
<tr>
<td>EXTKEYUSAGE_E</td>
<td>-247</td>
<td>Bad extended key usage value</td>
</tr>
<tr>
<td>WC_HW_E</td>
<td>-248</td>
<td>Error with hardware crypto use</td>
</tr>
<tr>
<td>WC_HW_WAIT_E</td>
<td>-249</td>
<td>Hardware waiting on resource</td>
</tr>
<tr>
<td>PSS_SALTLEN_E</td>
<td>-250</td>
<td>PSS length of salt is too long for hash</td>
</tr>
<tr>
<td>PRIME_GEN_E</td>
<td>-251</td>
<td>Failure finding a prime</td>
</tr>
<tr>
<td>BER_INDEF_E</td>
<td>-252</td>
<td>Cannot decode indefinite length BER</td>
</tr>
<tr>
<td>RSA_OUT_OF_RANGE_E</td>
<td>-253</td>
<td>Ciphertext to decrypt out of range</td>
</tr>
<tr>
<td>RSAPSS_PAT_FIPS_E</td>
<td>-254</td>
<td>RSA-PSS PAT failure</td>
</tr>
<tr>
<td>ECDSA_PAT_FIPS_E</td>
<td>-255</td>
<td>ECDSA PAT failure</td>
</tr>
<tr>
<td>DH_KAT_FIPS_E</td>
<td>-256</td>
<td>DH KAT failure</td>
</tr>
<tr>
<td>AESCCM_KAT_FIPS_E</td>
<td>-257</td>
<td>AESCCM KAT failure</td>
</tr>
<tr>
<td>SHA3_KAT_FIPS_E</td>
<td>-258</td>
<td>SHA-3 KAT failure</td>
</tr>
<tr>
<td>ECDHE_KAT_FIPS_E</td>
<td>-259</td>
<td>ECDHE KAT failure</td>
</tr>
<tr>
<td>AES_GCM_OVERFLOW_E</td>
<td>-260</td>
<td>AES-GCM invocation counter overflow</td>
</tr>
<tr>
<td>AES_CCM_OVERFLOW_E</td>
<td>-261</td>
<td>AES-CCM invocation counter overflow</td>
</tr>
<tr>
<td>RSA_KEY_PAIR_E</td>
<td>-262</td>
<td>RSA Key Pair-Wise consistency check fail</td>
</tr>
<tr>
<td>DH_CHECK_PRIVE_E</td>
<td>-263</td>
<td>DH check private key error</td>
</tr>
<tr>
<td>WC_AFALG_SOCK_E</td>
<td>-264</td>
<td>AF_ALG socket error</td>
</tr>
<tr>
<td>WC_DEVCRYPTO_E</td>
<td>-265</td>
<td>/dev/crypto error</td>
</tr>
<tr>
<td>ZLIB_INIT_ERROR</td>
<td>-266</td>
<td>Zlib init error</td>
</tr>
<tr>
<td>ZLIB_COMPRESS_ERROR</td>
<td>-267</td>
<td>Zlib compression error</td>
</tr>
<tr>
<td>ZLIB_DECOMPRESS_ERROR</td>
<td>-268</td>
<td>Zlib decompression error</td>
</tr>
<tr>
<td>PKCS7_NO_SIGNER_E</td>
<td>-269</td>
<td>No signer in PKCS7 signed data msg</td>
</tr>
<tr>
<td>WC_PKCS7_WANT_READ_E</td>
<td>-270</td>
<td>PKCS7 stream operation wants more input</td>
</tr>
<tr>
<td>CRYPTOCB_UNAVAILABLE</td>
<td>-271</td>
<td>Crypto callback unavailable</td>
</tr>
<tr>
<td>PKCS7_SIGNEEDS_CHECK</td>
<td>-272</td>
<td>Signature needs verified by caller</td>
</tr>
<tr>
<td>ASN_SELF_SIGNED_E</td>
<td>-275</td>
<td>ASN self-signed certificate error</td>
</tr>
<tr>
<td>MIN_CODE_E</td>
<td>-300</td>
<td>errors -101 - -299</td>
</tr>
<tr>
<td>INPUT_CASE_ERROR</td>
<td>-301</td>
<td>process input state error</td>
</tr>
<tr>
<td>PREFIX_ERROR</td>
<td>-302</td>
<td>bad index to key rounds</td>
</tr>
<tr>
<td>MEMORY_ERROR</td>
<td>-303</td>
<td>out of memory</td>
</tr>
<tr>
<td>VERIFY_FINISHED_ERROR</td>
<td>-304</td>
<td>verify problem on finished</td>
</tr>
<tr>
<td>VERIFY_MAC_ERROR</td>
<td>-305</td>
<td>verify mac problem</td>
</tr>
<tr>
<td>PARSE_ERROR</td>
<td>-306</td>
<td>parse error on header</td>
</tr>
<tr>
<td>UNKNOWN_HANDSHAKE_TYPE</td>
<td>-307</td>
<td>weird handshake type</td>
</tr>
<tr>
<td>SOCKET_ERROR_E</td>
<td>-308</td>
<td>error state on socket</td>
</tr>
<tr>
<td>SOCKET_NODATA</td>
<td>-309</td>
<td>expected data, not there</td>
</tr>
<tr>
<td>INCOMPLETE_DATA</td>
<td>-310</td>
<td>don’t have enough data to complete task</td>
</tr>
<tr>
<td>UNKNOWN_RECORD_TYPE</td>
<td>-311</td>
<td>unknown type in record hdr</td>
</tr>
<tr>
<td>DECRYPT_ERROR</td>
<td>-312</td>
<td>error during decryption</td>
</tr>
<tr>
<td>FATAL_ERROR</td>
<td>-313</td>
<td>revcd alert fatal error</td>
</tr>
<tr>
<td>ENCRYPT_ERROR</td>
<td>-314</td>
<td>error during encryption</td>
</tr>
<tr>
<td>FREAD_ERROR</td>
<td>-315</td>
<td>fread problem</td>
</tr>
<tr>
<td>NO_PEER_KEY</td>
<td>-316</td>
<td>need peer’s key</td>
</tr>
<tr>
<td>NO_PRIVATE_KEY</td>
<td>-317</td>
<td>need the private key</td>
</tr>
<tr>
<td>RSA_PRIVATE_ERROR</td>
<td>-318</td>
<td>error during rsa priv op</td>
</tr>
<tr>
<td>NO_DH_PARAMS</td>
<td>-319</td>
<td>server missing DH params</td>
</tr>
<tr>
<td>BUILD_MSG_ERROR</td>
<td>-320</td>
<td>build message failure</td>
</tr>
<tr>
<td>BAD_HELLO</td>
<td>-321</td>
<td>client hello malformed</td>
</tr>
<tr>
<td>DOMAIN_NAME_MISMATCH</td>
<td>-322</td>
<td>peer subject name mismatch</td>
</tr>
<tr>
<td>WANT_READ</td>
<td>-323</td>
<td>want read, call again</td>
</tr>
<tr>
<td>NOT_READY_ERROR</td>
<td>-324</td>
<td>handshake layer not ready</td>
</tr>
<tr>
<td>VERSION_ERROR</td>
<td>-326</td>
<td>record layer version error</td>
</tr>
<tr>
<td>WANT_WRITE</td>
<td>-327</td>
<td>want write, call again</td>
</tr>
<tr>
<td>BUFFER_ERROR</td>
<td>-328</td>
<td>malformed buffer input</td>
</tr>
<tr>
<td>VERIFY_CERT_ERROR</td>
<td>-329</td>
<td>verify cert error</td>
</tr>
<tr>
<td>VERIFY_SIGN_ERROR</td>
<td>-330</td>
<td>verify sign error</td>
</tr>
<tr>
<td>CLIENT_ID_ERROR</td>
<td>-331</td>
<td>psk client identity error</td>
</tr>
<tr>
<td>SERVER_HINT_ERROR</td>
<td>-332</td>
<td>psk server hint error</td>
</tr>
<tr>
<td>PSK_KEY_ERROR</td>
<td>-333</td>
<td>psk key error</td>
</tr>
<tr>
<td>GETTIME_ERROR</td>
<td>-337</td>
<td>gettimeofday failed ???</td>
</tr>
<tr>
<td>GETITIMER_ERROR</td>
<td>-338</td>
<td>getitimer failed ???</td>
</tr>
<tr>
<td>SIGACT_ERROR</td>
<td>-339</td>
<td>sigaction failed ???</td>
</tr>
<tr>
<td>SETITIMER_ERROR</td>
<td>-340</td>
<td>setitimer failed ???</td>
</tr>
<tr>
<td>LENGTH_ERROR</td>
<td>-341</td>
<td>record layer length error</td>
</tr>
<tr>
<td>PEER_KEY_ERROR</td>
<td>-342</td>
<td>cant decode peer key</td>
</tr>
<tr>
<td>ZERO_RETURN</td>
<td>-343</td>
<td>peer sent close notify</td>
</tr>
<tr>
<td>SIDE_ERROR</td>
<td>-344</td>
<td>wrong client/server type</td>
</tr>
<tr>
<td>NO_PEER_CERT</td>
<td>-345</td>
<td>peer didn’t send key</td>
</tr>
<tr>
<td>ECC_CURVETYPE_ERROR</td>
<td>-350</td>
<td>Bad ECC Curve Type</td>
</tr>
<tr>
<td>ECC_CURVE_ERROR</td>
<td>-351</td>
<td>Bad ECC Curve</td>
</tr>
<tr>
<td>ECC_PEERKEY_ERROR</td>
<td>-352</td>
<td>Bad Peer ECC Key</td>
</tr>
<tr>
<td>ECC_MAKEKEY_ERROR</td>
<td>-353</td>
<td>Bad Make ECC Key</td>
</tr>
<tr>
<td>ECC_EXPORT_ERROR</td>
<td>-354</td>
<td>Bad ECC Export Key</td>
</tr>
<tr>
<td>ECC_SHARED_ERROR</td>
<td>-355</td>
<td>Bad ECC Shared Secret</td>
</tr>
<tr>
<td>NOT_CA_ERROR</td>
<td>-357</td>
<td>Not CA cert error</td>
</tr>
<tr>
<td>BAD_CERT_MANAGER_ERROR</td>
<td>-359</td>
<td>Bad Cert Manager</td>
</tr>
<tr>
<td>OCSP_CERT_REVOKED</td>
<td>-360</td>
<td>OCSP Certificate revoked</td>
</tr>
<tr>
<td>CRL_CERT_REVOKED</td>
<td>-361</td>
<td>CRL Certificate revoked</td>
</tr>
<tr>
<td>CRL_MISSING</td>
<td>-362</td>
<td>CRL Not loaded</td>
</tr>
<tr>
<td>MONITOR_SETUP_E</td>
<td>-363</td>
<td>CRL Monitor setup error</td>
</tr>
<tr>
<td>THREAD_CREATE_E</td>
<td>-364</td>
<td>Thread Create Error</td>
</tr>
<tr>
<td>OCSP_NEED_URL</td>
<td>-365</td>
<td>OCSP need an URL for lookup</td>
</tr>
<tr>
<td>OCSP_CERT_UNKNOWN</td>
<td>-366</td>
<td>OCSP responder doesn’t know</td>
</tr>
<tr>
<td>OCSP_LOOKUP_FAIL</td>
<td>-367</td>
<td>OCSP lookup not successful</td>
</tr>
<tr>
<td>MAX_CHAIN_ERROR</td>
<td>-368</td>
<td>max chain depth exceeded</td>
</tr>
<tr>
<td>COOKIE_ERROR</td>
<td>-369</td>
<td>dtls cookie error</td>
</tr>
<tr>
<td>SEQUENCE_ERROR</td>
<td>-370</td>
<td>dtls sequence error</td>
</tr>
<tr>
<td>SUITES_ERROR</td>
<td>-371</td>
<td>suites pointer error</td>
</tr>
<tr>
<td>OUT_OF_ORDER_E</td>
<td>-373</td>
<td>out of order message</td>
</tr>
<tr>
<td>BAD_KEA_TYPE_E</td>
<td>-374</td>
<td>bad KEA type found</td>
</tr>
<tr>
<td>SANITY_CIPHER_E</td>
<td>-375</td>
<td>sanity check on cipher error</td>
</tr>
<tr>
<td>RECV_OVERFLOW_E</td>
<td>-376</td>
<td>RXCB returned more than rqed</td>
</tr>
<tr>
<td>GEN_COOKIE_E</td>
<td>-377</td>
<td>Generate Cookie Error</td>
</tr>
<tr>
<td>NO_PEER_VERIFY</td>
<td>-378</td>
<td>Need peer cert verify Error</td>
</tr>
<tr>
<td>FWRITE_ERROR</td>
<td>-379</td>
<td>fwrite problem</td>
</tr>
<tr>
<td>CACHE_MATCH_ERROR</td>
<td>-380</td>
<td>cache hrd match error</td>
</tr>
<tr>
<td>UNKNOWN_SNI_HOST_NAME_E</td>
<td>-381</td>
<td>Unrecognized host name Error</td>
</tr>
<tr>
<td>UNKNOWN_MAX_FRAG_LEN_E</td>
<td>-382</td>
<td>Unrecognized max frag len Error</td>
</tr>
<tr>
<td>KEYUSE_SIGNATURE_E</td>
<td>-383</td>
<td>KeyUse digSignature error</td>
</tr>
<tr>
<td>KEYUSE_ENCIPHER_E</td>
<td>-385</td>
<td>KeyUse KeyEncipher error</td>
</tr>
<tr>
<td>EXTKEYUSE_AUTH_E</td>
<td>-386</td>
<td>ExtKeyUse server</td>
</tr>
<tr>
<td>SEND_OOB_READ_E</td>
<td>-387</td>
<td>Send Cb out of bounds read</td>
</tr>
<tr>
<td>SECURE_RENEGOTIATION_E</td>
<td>-388</td>
<td>Invalid renegotiation info</td>
</tr>
<tr>
<td>SESSION_TICKET_LEN_E</td>
<td>-389</td>
<td>Session Ticket too large</td>
</tr>
<tr>
<td>SESSION_TICKET_EXPECT_E</td>
<td>-390</td>
<td>Session Ticket missing</td>
</tr>
<tr>
<td>SCR_DIFFERENT_CERT_E</td>
<td>-391</td>
<td>SCR Different cert error</td>
</tr>
<tr>
<td>SESSION_SECRET_CB_E</td>
<td>-392</td>
<td>Session secret CB fcn failure</td>
</tr>
<tr>
<td>NO_CHANGE_CIPHER_E</td>
<td>-393</td>
<td>Finished before change cipher</td>
</tr>
<tr>
<td>SANITY_MSG_E</td>
<td>-394</td>
<td>Sanity check on msg order error</td>
</tr>
<tr>
<td>DUPLICATE_MST_E</td>
<td>-395</td>
<td>Duplicate message error</td>
</tr>
<tr>
<td>SNI_UNSUPPORTED</td>
<td>-396</td>
<td>SSL 3.0 does not support SNI</td>
</tr>
<tr>
<td>SOCKET_PEER_CLOSED_E</td>
<td>-397</td>
<td>Underlying transport closed</td>
</tr>
<tr>
<td>BAD_TICKET_KEY_CB_SZ</td>
<td>-398</td>
<td>Bad session ticket key cb size</td>
</tr>
<tr>
<td>BAD_TICKET_MSG_SZ</td>
<td>-399</td>
<td>Bad session ticket msg size</td>
</tr>
<tr>
<td>BAD_TICKET_ENCRYPT</td>
<td>-400</td>
<td>Bad user ticket encrypt</td>
</tr>
<tr>
<td>DH_KEY_SIZE_E</td>
<td>-401</td>
<td>DH key too small</td>
</tr>
<tr>
<td>SNI_ABSENT_ERROR</td>
<td>-402</td>
<td>No SNI request</td>
</tr>
<tr>
<td>RSA_SIGN_FAULT</td>
<td>-403</td>
<td>RSA sign fault</td>
</tr>
<tr>
<td>HANDSHAKE_SIZE_ERROR</td>
<td>-404</td>
<td>Handshake message too large</td>
</tr>
<tr>
<td>UNKNOWN_ALPN_PROTOCOL_NAME_E</td>
<td>-405</td>
<td>Unrecognized protocol name error</td>
</tr>
<tr>
<td>BAD_CERTIFICATE_STATUS_ERROR</td>
<td>-406</td>
<td>Bad certificate status message</td>
</tr>
<tr>
<td>OCSP_INVALID_STATUS</td>
<td>-407</td>
<td>Invalid OCSP status</td>
</tr>
<tr>
<td>OCSP_WANT_READ</td>
<td>-408</td>
<td>OCSP callback response</td>
</tr>
<tr>
<td>RSA_KEY_SIZE_E</td>
<td>-409</td>
<td>RSA key too small</td>
</tr>
<tr>
<td>ECC_KEY_SIZE_E</td>
<td>-410</td>
<td>ECC key too small</td>
</tr>
<tr>
<td>DTLS_EXPORT_VER_E</td>
<td>-411</td>
<td>Export version error</td>
</tr>
<tr>
<td>INPUT_SIZE_E</td>
<td>-412</td>
<td>Input size too big error</td>
</tr>
<tr>
<td>CTX_INIT_MUTEX_E</td>
<td>-413</td>
<td>Initialize ctx mutex error</td>
</tr>
<tr>
<td>EXT_MASTER_SECRET_NEEDED_E</td>
<td>-414</td>
<td>Need EMS enabled to resume</td>
</tr>
<tr>
<td>DTLS_POOL_SZ_E</td>
<td>-415</td>
<td>Exceeded DTLS pool size</td>
</tr>
<tr>
<td>DECODE_E</td>
<td>-416</td>
<td>Decode handshake message error</td>
</tr>
<tr>
<td>HTTP_TIMEOUT</td>
<td>-417</td>
<td>HTTP timeout for OCSP or CRL req</td>
</tr>
<tr>
<td>WRITE_DUP_READ_E</td>
<td>-418</td>
<td>Write dup write side can’t read</td>
</tr>
<tr>
<td>WRITE_DUP_WRITE_E</td>
<td>-419</td>
<td>Write dup read side can’t write</td>
</tr>
<tr>
<td>INVALID_CERT_CTX_E</td>
<td>-420</td>
<td>TLS cert ctx not matching</td>
</tr>
<tr>
<td>BAD_KEY_SHARE_DATA</td>
<td>-421</td>
<td>Key share data invalid</td>
</tr>
<tr>
<td>MISSING_HANDSHAKE_DATA</td>
<td>-422</td>
<td>Handshake message missing data</td>
</tr>
<tr>
<td>BAD_BINDER</td>
<td>-423</td>
<td>Binder does not match</td>
</tr>
<tr>
<td>EXT_NOT_ALLOWED</td>
<td>-424</td>
<td>Extension not allowed in msg</td>
</tr>
<tr>
<td>INVALID_PARAMETER</td>
<td>-425</td>
<td>Security parameter invalid</td>
</tr>
<tr>
<td>MCAST_HIGHWATER_CB_E</td>
<td>-426</td>
<td>Multicast highwater cb error</td>
</tr>
<tr>
<td>ALERT_COUNT_E</td>
<td>-427</td>
<td>Alert count exceeded error</td>
</tr>
<tr>
<td>EXT_MISSING</td>
<td>-428</td>
<td>Required extension not found</td>
</tr>
<tr>
<td>UNSUPPORTED_EXTENSION</td>
<td>-429</td>
<td>TLSX not requested by client</td>
</tr>
<tr>
<td>PRF_MISSING</td>
<td>-430</td>
<td>PRF not compiled in</td>
</tr>
<tr>
<td>DTLS_RETX_OVER_TX</td>
<td>-431</td>
<td>Retransmit DTLS flight over</td>
</tr>
<tr>
<td>DH_PARAMS_NOT_FFDHE_E</td>
<td>-432</td>
<td>DH params from server not FFDHE</td>
</tr>
<tr>
<td>TCA_INVALID_ID_TYPE</td>
<td>-433</td>
<td>TLSX TCA ID type invalid</td>
</tr>
<tr>
<td>TCA_ABSENT_ERROR</td>
<td>-434</td>
<td>TLSX</td>
</tr>
<tr>
<td>UNSUPPORTED_SUITE</td>
<td>-500</td>
<td>Unsupported cipher suite</td>
</tr>
<tr>
<td>MATCH_SUITE_ERROR</td>
<td>-501</td>
<td>Can’t match cipher suite</td>
</tr>
<tr>
<td>COMPRESSION_ERROR</td>
<td>-502</td>
<td>Compression mismatch</td>
</tr>
<tr>
<td>KEY_SHARE_ERROR</td>
<td>-503</td>
<td>Key share mismatch</td>
</tr>
<tr>
<td>POST_HAND_AUTH_ERROR</td>
<td>-504</td>
<td>Client won’t do post-hand auth</td>
</tr>
<tr>
<td>HRR_COOKIE_ERROR</td>
<td>-505</td>
<td>HRR msg cookie mismatch</td>
</tr>
</tbody>
</table>

### Function Reference:

<a id="AN_FUNC_AT_TLS_TLSC"></a>
#### WINC_CmdTLSC

##### Description

This function is used to read or set the TLS configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdTLSC
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t optConf
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optConf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Configuration number.<br />
</p>
<p>optConf will be ignored if its value is<br />
WINC_CMDTLSC_CONF_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDTLSC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response          | Description   |
|-------------------|---------------|
| \<CONF\>,\<CONF\> | List response |
| \<ID\>,\<VAL\>    | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Valid range is 1 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_TLS_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_CA_CERT_NAME"></span> 1</p></td>
<td style="text-align: left;"><p>CA_CERT_NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>CA certificate name<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_CERT_NAME"></span> 2</p></td>
<td style="text-align: left;"><p>CERT_NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Certificate name<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_PRI_KEY_NAME"></span> 3</p></td>
<td style="text-align: left;"><p>PRI_KEY_NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Private key name<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_PRI_KEY_PASSWORD"></span> 4</p></td>
<td style="text-align: left;"><p>PRI_KEY_PASSWORD</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Private key password<br />
Maximum length of string is 64<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_SERVER_NAME"></span> 5</p></td>
<td style="text-align: left;"><p>SERVER_NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Server name<br />
Maximum length of string is 256<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_DOMAIN_NAME"></span> 6</p></td>
<td style="text-align: left;"><p>DOMAIN_NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Domain name<br />
Maximum length of string is 256<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_CIPHER_SUITES_IDX"></span> 7</p></td>
<td style="text-align: left;"><p>CIPHER_SUITES_IDX</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Cipher suite index<br />
<br />
Valid range is 1 to 2<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_DH_PARAM_NAME"></span> 8</p></td>
<td style="text-align: left;"><p>DH_PARAM_NAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Server Diffie-Hellman parameters identifier<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_EXTCRYPTO_OPS"></span> 20</p></td>
<td style="text-align: left;"><p>EXTCRYPTO_OPS</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Crypto operations to be done externally<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NONE</p></td>
<td style="text-align: left;"><p>None.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SIGN</p></td>
<td style="text-align: left;"><p>Signing.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>SIGN_TYPES</p></td>
<td style="text-align: left;"><p>INTEGER<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Types of signing to be done externally<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ECDSA</p></td>
<td style="text-align: left;"><p>ECDSA.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_PEER_AUTH"></span> 40</p></td>
<td style="text-align: left;"><p>PEER_AUTH</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Peer authentication<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Peer authentication is disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Peer authentication is enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_PEER_DOMAIN_VERIFY"></span> 41</p></td>
<td style="text-align: left;"><p>PEER_DOMAIN_VERIFY</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Peer domain verification<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Peer domain name verification is disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Peer domain name verification is enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_SERVER_RENEG_INFO"></span> 42</p></td>
<td style="text-align: left;"><p>SERVER_RENEG_INFO</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Client mode: require renegotiation info from server<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NOT REQUIRED</p></td>
<td style="text-align: left;"><p>Do not require renegotiation info from server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>REQUIRED</p></td>
<td style="text-align: left;"><p>Require renegotiation info from server.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_TLSC_STORE_ID_SESSION_CACHING"></span> 43</p></td>
<td style="text-align: left;"><p>SESSION_CACHING</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Client mode: cache and reuse session IDs<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Do not reuse session IDs.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Attempt to reuse session IDs.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_TLS_TLSCDA"></a>
#### WINC_CmdTLSCDA

##### Description

This function is used to read or set the TLS configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdTLSCDA
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t conf
        const uint8_t* pDigest
        size_t lenDigest
        uint8_t optAlgo
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>conf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Configuration number.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pDigest</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Hash digest.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenDigest</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pDigest.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optAlgo</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Hash algorithm.<br />
</p>
<p>optAlgo will be ignored if its value is<br />
WINC_CMDTLSCDA_ALGO_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response          | Description   |
|-------------------|---------------|
| \<CONF\>,\<CONF\> | List response |
| \<ID\>,\<VAL\>    | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Valid range is 1 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_TLS_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>PEER_CERT_DIGESTS</p></td>
<td style="text-align: left;"><p>Complex Value<sup>1</sup><br />
</p></td>
<td style="text-align: left;"><p>List of hash digest/algorithm pairs<br />
This is a multiple value parameter<br />
with an ID range 9.0 to 9.3<br />
</p></td>
</tr>
</tbody>
</table>

| No. | Complex Value       | Description                |
|-----|---------------------|----------------------------|
| 1   | \<DIGEST\>,\<ALGO\> | Hash digest/algorithm pair |

**Complex Value Syntax**

<table>
<caption>Complex Value Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;DIGEST&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Hash digest<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALGO&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Hash algorithm<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_TLS_TLSCSC"></a>
#### WINC_CmdTLSCSC

##### Description

This function is used to read or set the TLS cipher suite configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdTLSCSC
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t optCslIdx
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optCslIdx</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Cipher suite list index.<br />
</p>
<p>optCslIdx will be ignored if its value is<br />
WINC_CMDTLSCSC_CSL_IDX_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDTLSCSC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_TLS_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CIPHER_SUITES</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Cipher suites<br />
<br />
Positive unsigned 16-bit value<br />
This is a multiple value parameter<br />
with an ID range 1.0 to 1.31<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>CIPHER_SUITES_AVAIL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Cipher suites available<br />
<br />
Positive unsigned 16-bit value<br />
This is a multiple value parameter<br />
with an ID range 2.0 to 2.31<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_TLSERR

##### Description

**TLS error.**

| AEC                     | Description |
|-------------------------|-------------|
| \<CONF\>,\<ERROR_CODE\> | TLS error   |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Valid range is 1 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_TLS_DIGEST"></a>
**Peer certificate digest pinning with [WINC_CmdTLSCDA](#AN_FUNC_AT_TLS_TLSCDA)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Add SHA1 000102... certificate digest
    APP->>API: WINC_CmdTLSCDA(1,[000102030405060708090A0B0C0D0E0F00010203],1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Add SHA1 101112... certificate digest
    APP->>API: WINC_CmdTLSCDA(1,[101112131415161718191A1B1C1D1E1F10111213],1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: List certificate digests
    APP->>API: WINC_CmdTLSC(1,9)
    API->>APP: Response:WINC_CMD_ID_TLSC(9.0,[000102030405060708090A0B0C0D0E0F00010203],1)
    API->>APP: Response:WINC_CMD_ID_TLSC(9.1,[101112131415161718191A1B1C1D1E1F10111213],1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Clear certificate digest list
    APP->>API: WINC_CmdTLSCDA(1,[])
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: List certificate digests
    APP->>API: WINC_CmdTLSC(1,9)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
```

---
<a id="AN_MOD_WAP"></a>
## WAP (Module ID = 18)

### Function Reference:

#### WINC_CmdWAPC

##### Description

This function is used to read or set the WINC’s hotspot access point configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdWAPC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDWAPC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_WAP_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SSID</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Network Name<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>SEC_TYPE</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Security Type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OPEN</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2_PERS_MIXED</p></td>
<td style="text-align: left;"><p>WPA2 Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2_PERS</p></td>
<td style="text-align: left;"><p>WPA2 Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3_PERS_TRANS</p></td>
<td style="text-align: left;"><p>WPA3 Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3_PERS</p></td>
<td style="text-align: left;"><p>WPA3 Personal.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>CREDENTIALS</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Credentials required for connecting to the network of the security type specified<br />
Maximum length of string is 128<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>CHANNEL</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The channel on which to set up the network<br />
<br />
Valid range is 1 to 13<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>HIDDEN</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Visibility of the network<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>VISIBLE</p></td>
<td style="text-align: left;"><p>Not hidden, SSID is broadcast in beacons.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>HIDDEN</p></td>
<td style="text-align: left;"><p>Hidden, SSID is not broadcast.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>NETIF_IDX</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Network interface index<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>REKEY_INTERVAL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Specify the time in seconds that must pass before each re-key attempt<br />
<br />
Valid range is 60 to 86400<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>50</p></td>
<td style="text-align: left;"><p>MFP_TYPE</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Management Frame Protection configuration<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>MFP Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>MFP Enabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>REQUIRED</p></td>
<td style="text-align: left;"><p>MFP Required.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdWAP

##### Description

This function is used to enable the WINC’s hotspot access point functionality.

    bool WINC_CmdWAP
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optState
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optState</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>State of the hotspot feature.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLE</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLE</p></td>
<td style="text-align: left;"><p>Enable.</p></td>
</tr>
</tbody>
</table>
<p>optState will be ignored if its value is<br />
WINC_CMDWAP_STATE_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response  | Description                |
|-----------|----------------------------|
| \<STATE\> | Query state (disconnected) |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Connected state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_WAPAIP

##### Description

**STA IP address assignment.**

| AEC                         | Description                  |
|-----------------------------|------------------------------|
| \<ASSOC_ID\>,\<IP_ADDRESS\> | Assignment of STA IP address |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;IP_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>IP address assigned<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_WAPSC

##### Description

**STA connected.**

| AEC                          | Description     |
|------------------------------|-----------------|
| \<ASSOC_ID\>,\<MAC_ADDRESS\> | Station connect |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MAC_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>MAC address of the STA<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_WAPSD

##### Description

**STA disconnected.**

| AEC                          | Description        |
|------------------------------|--------------------|
| \<ASSOC_ID\>,\<MAC_ADDRESS\> | Station disconnect |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MAC_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>MAC address of the STA<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_WAPERR

##### Description

**AP error.**

| AEC            | Description |
|----------------|-------------|
| \<ERROR_CODE\> | AP error    |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
## WSCN (Module ID = 19)

### Function Reference:

<a id="AN_FUNC_AT_WSCN_WSCNC"></a>
#### WINC_CmdWSCNC

##### Description

This function is used to modify or query the behavior of the active scanning function.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdWSCNC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDWSCNC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_WSCN_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CHANNEL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Channel to scan (or 0 for all channels)<br />
<br />
Valid range is 1 to 13<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>ACT_SLOT_TIME</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>The time in milliseconds to wait for probe responses<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>PASV_SLOT_TIME</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>The time in milliseconds to wait for beacons<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>NUM_SLOTS</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Number of scan slots<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>PROBES_PER_SLOT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Number of probes sent per active slot<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>RSSI_THRESH</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>RSSI threshold (or 0 for none)<br />
<br />
Signed 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>SEC_FILTER</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Security filter, bitmask of:<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0x01</p></td>
<td style="text-align: left;"><p>PERS</p></td>
<td style="text-align: left;"><p>Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x02</p></td>
<td style="text-align: left;"><p>ENT</p></td>
<td style="text-align: left;"><p>Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x04</p></td>
<td style="text-align: left;"><p>OPEN</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x08</p></td>
<td style="text-align: left;"><p>NA</p></td>
<td style="text-align: left;"><p>Unknown or unsupported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x10</p></td>
<td style="text-align: left;"><p>WPA</p></td>
<td style="text-align: left;"><p>WPA or WPA2 Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x20</p></td>
<td style="text-align: left;"><p>WPA2</p></td>
<td style="text-align: left;"><p>WPA2.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x40</p></td>
<td style="text-align: left;"><p>WPA3</p></td>
<td style="text-align: left;"><p>WPA3 or WPA3 Transition Mode.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>ASYNC_NOTIFY</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Asynchronous notification<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NO_AECS</p></td>
<td style="text-align: left;"><p>No scan indication AECs are generated.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>USE_AECS</p></td>
<td style="text-align: left;"><p>Indication AECs are generated.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>FILT_LIST</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>SSID filter list<br />
This is a multiple value parameter<br />
with an ID range 10.0 to 10.3<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>CHANMASK24</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Scan-all channel mask (2.4 GHz)<br />
</p>
<table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><p><sup>15</sup><br />
-</p></td>
<td style="text-align: center;"><p><sup>14</sup><br />
-</p></td>
<td style="text-align: center;"><p><sup>13</sup><br />
CH14</p></td>
<td style="text-align: center;"><p><sup>12</sup><br />
CH13</p></td>
<td style="text-align: center;"><p><sup>11</sup><br />
CH12</p></td>
<td style="text-align: center;"><p><sup>10</sup><br />
CH11</p></td>
<td style="text-align: center;"><p><sup>9</sup><br />
CH1</p></td>
<td style="text-align: center;"><p><sup>8</sup><br />
CH9</p></td>
</tr>
<tr>
<td style="text-align: center;"><p><sup>7</sup><br />
CH8</p></td>
<td style="text-align: center;"><p><sup>6</sup><br />
CH7</p></td>
<td style="text-align: center;"><p><sup>5</sup><br />
CH6</p></td>
<td style="text-align: center;"><p><sup>4</sup><br />
CH5</p></td>
<td style="text-align: center;"><p><sup>3</sup><br />
CH4</p></td>
<td style="text-align: center;"><p><sup>2</sup><br />
CH3</p></td>
<td style="text-align: center;"><p><sup>1</sup><br />
CH2</p></td>
<td style="text-align: center;"><p><sup>0</sup><br />
CH1</p></td>
</tr>
</tbody>
</table>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0x0001</p></td>
<td style="text-align: left;"><p>CH1</p></td>
<td style="text-align: left;"><p>Channel 1 - 2412 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0002</p></td>
<td style="text-align: left;"><p>CH2</p></td>
<td style="text-align: left;"><p>Channel 2 - 2417 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0004</p></td>
<td style="text-align: left;"><p>CH3</p></td>
<td style="text-align: left;"><p>Channel 3 - 2422 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0008</p></td>
<td style="text-align: left;"><p>CH4</p></td>
<td style="text-align: left;"><p>Channel 4 - 2427 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0010</p></td>
<td style="text-align: left;"><p>CH5</p></td>
<td style="text-align: left;"><p>Channel 5 - 2432 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0020</p></td>
<td style="text-align: left;"><p>CH6</p></td>
<td style="text-align: left;"><p>Channel 6 - 2437 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0040</p></td>
<td style="text-align: left;"><p>CH7</p></td>
<td style="text-align: left;"><p>Channel 7 - 2442 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0080</p></td>
<td style="text-align: left;"><p>CH8</p></td>
<td style="text-align: left;"><p>Channel 8 - 2447 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0100</p></td>
<td style="text-align: left;"><p>CH9</p></td>
<td style="text-align: left;"><p>Channel 9 - 2452 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0200</p></td>
<td style="text-align: left;"><p>CH10</p></td>
<td style="text-align: left;"><p>Channel 10 - 2457 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0400</p></td>
<td style="text-align: left;"><p>CH11</p></td>
<td style="text-align: left;"><p>Channel 11 - 2462 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0800</p></td>
<td style="text-align: left;"><p>CH12</p></td>
<td style="text-align: left;"><p>Channel 12 - 2467 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x1000</p></td>
<td style="text-align: left;"><p>CH13</p></td>
<td style="text-align: left;"><p>Channel 13 - 2472 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x2000</p></td>
<td style="text-align: left;"><p>CH14</p></td>
<td style="text-align: left;"><p>Channel 14 - 2485 MHz.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>SCAN_RESULTS</p></td>
<td style="text-align: left;"><p>Complex Value<sup>1</sup><br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Top scan results from previous scan, ordered by RSSI<br />
This is a multiple value parameter<br />
with an ID range 20.0 to 20.7<br />
</p></td>
</tr>
</tbody>
</table>

| No. | Complex Value                                        | Description    |
|-----|------------------------------------------------------|----------------|
| 1   | \<RSSI\>,\<SEC_TYPE\>,\<CHANNEL\>,\<BSSID\>,\<SSID\> | Scan indicator |

**Complex Value Syntax**

<table>
<caption>Complex Value Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;RSSI&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Received signal strength<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEC_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Recommended security type to use when connecting to this AP<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>-1</p></td>
<td style="text-align: left;"><p>NA</p></td>
<td style="text-align: left;"><p>Unknown or unsupported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OPEN</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2_PER_MM</p></td>
<td style="text-align: left;"><p>WPA2-Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2_PER</p></td>
<td style="text-align: left;"><p>WPA2-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3_PER_TM</p></td>
<td style="text-align: left;"><p>WPA3-Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3_PER</p></td>
<td style="text-align: left;"><p>WPA3-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>WPA2_ENT_MM</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>WPA2_ENT</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>WPA3_ENT_TM</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>WPA3_ENT</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CHANNEL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The channel number of the detected device<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BSSID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of detected device<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SSID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>SSID of detected device<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdWSCN

##### Description

This function is used to scan for infrastructure networks in range of the WINC.

    bool WINC_CmdWSCN
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t actPasv
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>actPasv</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Flag indicating active or passive scanning.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PASSIVE</p></td>
<td style="text-align: left;"><p>Passive scanning.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ACTIVE</p></td>
<td style="text-align: left;"><p>Active scanning.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_WSCNIND

##### Description

**Scan results.**

| AEC                                                  | Description    |
|------------------------------------------------------|----------------|
| \<RSSI\>,\<SEC_TYPE\>,\<CHANNEL\>,\<BSSID\>,\<SSID\> | Scan indicator |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;RSSI&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Received signal strength<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEC_TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Recommended security type to use when connecting to this AP<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>-1</p></td>
<td style="text-align: left;"><p>NA</p></td>
<td style="text-align: left;"><p>Unknown or unsupported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OPEN</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2_PER_MM</p></td>
<td style="text-align: left;"><p>WPA2-Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2_PER</p></td>
<td style="text-align: left;"><p>WPA2-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3_PER_TM</p></td>
<td style="text-align: left;"><p>WPA3-Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3_PER</p></td>
<td style="text-align: left;"><p>WPA3-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>WPA2_ENT_MM</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>WPA2_ENT</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>WPA3_ENT_TM</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>WPA3_ENT</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CHANNEL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The channel number of the detected device<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BSSID&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of detected device<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SSID&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>SSID of detected device<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_WSCNDONE

##### Description

**Scan completed.**

| AEC             | Description   |
|-----------------|---------------|
| \<NUM_RESULTS\> | Scan complete |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;NUM_RESULTS&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of results returned in this scan operation<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_WSCN_SECURITY"></a>
**Scan for Access Points and filter by security type**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Query security filter
    APP->>API: WINC_CmdWSCNC(7)
    Note left of API: Security filter 0x77 (all supported security types)
    API->>APP: Response:WINC_CMD_ID_WSCNC(=7,0x77)
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
    Note right of APP: Scan for Access Points
    APP->>API: WINC_CmdWSCN(1)
    API->>APP: Status:WINC_CMD_ID_WSCN(OK)
    Note left of API: AP on network "SSID1" found on channel 11. For connecting, the recommended security type is WPA2-Enterprise Mixed Mode
    API->>APP: AEC:WINC_AEC_ID_WSCNIND(-38,6,11,"00:01:02:03:04:05","SSID1")
    Note left of API: AP on network "SSID1" found on channel 6. For connecting, the recommended security type is WPA2-Enterprise Mixed Mode
    API->>APP: AEC:WINC_AEC_ID_WSCNIND(-38,6,6,"00:02:04:06:08:0A","SSID1")
    Note left of API: AP on network "SSID2" found on channel 1. For connecting, the recommended security type is WPA3-Personal Transition Mode
    API->>APP: AEC:WINC_AEC_ID_WSCNIND(-40,4,1,"00:03:06:09:0C:0F","SSID2")
    Note left of API: AP on network "SSID3" found on channel 6. For connecting, the recommended security type is WPA3-Personal
    API->>APP: AEC:WINC_AEC_ID_WSCNIND(-35,5,6,"00:04:08:0C:10:14","SSID3")
    Note left of API: Scan completed, 4 results found
    API->>APP: AEC:WINC_AEC_ID_WSCNDONE(4)
    Note right of APP: Set security filter to WPA2-Personal
    APP->>API: WINC_CmdWSCNC(7,0x21)
    Note right of APP: Scan for Access Points
    APP->>API: WINC_CmdWSCN(1)
    API->>APP: Status:WINC_CMD_ID_WSCN(OK)
    Note left of API: AP on network "SSID2" found on channel 1. For connecting, the recommended security type is WPA3-Personal Transition Mode
    API->>APP: AEC:WINC_AEC_ID_WSCNIND(-41,4,1,"00:03:06:09:0C:0F","SSID2")
    Note left of API: AP on network "SSID3" found on channel 6. For connecting, the recommended security type is WPA3-Personal
    API->>APP: AEC:WINC_AEC_ID_WSCNIND(-36,5,6,"00:04:08:0C:10:14","SSID3")
    Note left of API: Scan completed, 2 results found
    API->>APP: AEC:WINC_AEC_ID_WSCNDONE(2)
    Note right of APP: Set security filter to WPA3-Personal or WPA3-Personal Transition Mode
    APP->>API: WINC_CmdWSCNC(7,0x41)
    Note right of APP: Scan for Access Points
    APP->>API: WINC_CmdWSCN(1)
    API->>APP: Status:WINC_CMD_ID_WSCN(OK)
    Note left of API: AP on network "SSID3" found on channel 6. For connecting, the recommended security type is WPA3-Personal
    API->>APP: AEC:WINC_AEC_ID_WSCNIND(-35,5,6,"00:04:08:0C:10:14","SSID3")
    Note left of API: Scan completed, 1 result found
    API->>APP: AEC:WINC_AEC_ID_WSCNDONE(1)
    Note right of APP: Set security filter to WPA2-Enterprise
    APP->>API: WINC_CmdWSCNC(7,0x22)
    Note right of APP: Scan for Access Points
    APP->>API: WINC_CmdWSCN(1)
    API->>APP: Status:WINC_CMD_ID_WSCN(OK)
    Note left of API: Scan completed, 0 results found
    API->>APP: AEC:WINC_AEC_ID_WSCNDONE(0)
    Note right of APP: Query security filter
    APP->>API: WINC_CmdWSCNC(7)
    Note left of API: Security filter 0x22 (WPA2-Enterprise)
    API->>APP: Response:WINC_CMD_ID_WSCNC(=7,0x22)
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
```

<a id="EXAMPLE_286d6c7f74c01a7bacc3d6fcaa240ad067b1f736"></a>
**Setting SSID filter with [WINC_CmdWSCNC](#AN_FUNC_AT_WSCN_WSCNC)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Add SSID1 to filter list
    APP->>API: WINC_CmdWSCNC(10,"SSID1")
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
    Note right of APP: Add SSID2 to filter list
    APP->>API: WINC_CmdWSCNC(10,"SSID2")
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
    Note right of APP: Add SSID3 to filter list
    APP->>API: WINC_CmdWSCNC(10,"SSID3")
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
    Note right of APP: List all filters
    APP->>API: WINC_CmdWSCNC(10)
    API->>APP: Response:WINC_CMD_ID_WSCNC(10.0,"SSID1")
    API->>APP: Response:WINC_CMD_ID_WSCNC(10.1,"SSID2")
    API->>APP: Response:WINC_CMD_ID_WSCNC(10.2,"SSID3")
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
    Note right of APP: Remove second filter entry (SSID2)
    APP->>API: WINC_CmdWSCNC(10.1,"")
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
    Note right of APP: List all filters
    APP->>API: WINC_CmdWSCNC(10)
    API->>APP: Response:WINC_CMD_ID_WSCNC(10.0,"SSID1")
    API->>APP: Response:WINC_CMD_ID_WSCNC(10.1,"SSID3")
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
    Note right of APP: Remove all filters
    APP->>API: WINC_CmdWSCNC(10,"")
    API->>APP: Status:WINC_CMD_ID_WSCNC(OK)
```

---
<a id="AN_MOD_WSTA"></a>
## WSTA (Module ID = 20)

### Introduction

The WINCS02 supports a wide range of features when operating as a Wi-Fi station (STA). It is designed for robust connectivity, security, and seamless network integration in a variety of applications.

The [WSTA](#AN_MOD_WSTA) module is used to configure the STA, control STA connection and get information about the STA.

#### Configuring the STA

Set STA parameters using the [WINC_CmdWSTAC](#AN_FUNC_AT_WSTA_WSTAC) function.

In order to connect the STA to an Access Point (AP), the following parameters must be set:

- The AP’s network name (SSID): [SSID](#AN_FUNC_WSTAC_STORE_ID_SSID)

- The security type (Open, WPA Personal or WPA Enterprise): [SEC_TYPE](#AN_FUNC_WSTAC_STORE_ID_SEC_TYPE)

- The security credentials (depending on security type)

Other parameters are optional, with default behaviour if they are not set:

- The AP’s Wi-Fi channel (1-13 or "any"; defaults to "any"): [CHANNEL](#AN_FUNC_WSTAC_STORE_ID_CHANNEL)

- The AP’s BSSID: [BSSID](#AN_FUNC_WSTAC_STORE_ID_BSSID)

- Management Frame Protection configuration (disabled, enabled or required; defaults to enabled): [MFP_TYPE](#AN_FUNC_WSTAC_STORE_ID_MFP_TYPE)

- Disabling of WPA3 Transition modes (defaults to "not modified"): [WPA3_TD](#AN_FUNC_WSTAC_STORE_ID_WPA3_TD)

- Connection attempt timeout (defaults to 100ms): [CONN_TIMEOUT](#AN_FUNC_WSTAC_STORE_ID_CONN_TIMEOUT)

- Roaming configuration (off, layer 2, or layer 3; defaults to layer 3): [ROAMING](#AN_FUNC_WSTAC_STORE_ID_ROAMING)

##### Security types and credentials

Open security provides no authentication or encryption. There are no security credentials to set.

WPA Personal security provides authentication and encryption via a password. WPA2 and WPA3 are supported, including transition and mixed modes. The credentials parameter must be set to the AP’s WPA Personal password: [CREDENTIALS](#AN_FUNC_WSTAC_STORE_ID_CREDENTIALS)

WPA Enterprise security provides encryption and various methods for authentication. WPA2 and WPA3 are supported, including transition and mixed modes. See the WPA Enterprise section below for further information about how to set authentication methods and security credentials.

---
##### Roaming

The WINCS02 STA supports Simple Roaming, which enables faster handover between Access Points within an ESSID for maintained connectivity.

Roaming can be configured at two different layers:

- Layer 2 roaming - moving to another SSID, leaving layers 3 (IP) and above unchanged

- Layer 3 roaming - as above but also reconfiguring layer 3 via DHCP

#### Controlling STA connection

Once the STA has been configured appropriately, start and stop the STA connection using the [WINC_CmdWSTA](#AN_FUNC_AT_WSTA_WSTA) function.

#### STA information

Query the STA parameters using the [WINC_CmdWSTAC](#AN_FUNC_AT_WSTA_WSTAC) function.

Query the STA status using the [WINC_CmdWSTA](#AN_FUNC_AT_WSTA_WSTA) function.

During connection:

- The [WINC_AEC_ID_WSTALU](#AN_AEC_AT_WSTA_WSTALU) and [WINC_AEC_ID_WSTALD](#AN_AEC_AT_WSTA_WSTALD) AECs indicate the Wi-Fi link being established ("up") or lost ("down") respectively. The [WINC_AEC_ID_WSTAROAM](#AN_AEC_AT_WSTA_WSTAROAM) AEC indicates a layer 2 roam event (connection lost and regained, possibly to a different AP).

- The [WINC_AEC_ID_WSTAAIP](#AN_AEC_AT_WSTA_WSTAAIP) AEC indicates the IP address assigned to the STA. Layer 3 roam events may cause this AEC to be received multiple times, whenever the IP address changes.

---
#### WPA Enterprise

WPA Enterprise significantly enhances Wi-Fi security by using an external authentication server (typically a RADIUS server) to perform user or device authentication dynamically. This process utilises the Extensible Authentication Protocol (EAP), enabling flexible authentication mechanisms beyond entering a simple shared password.

WPA Enterprise typically uses a **two-step process**:

1.  **Establish a secure encrypted tunnel between the Wi-Fi client (STA) and the authentication server.** A TLS (Transport Layer Security) handshake allows the client to authenticate the server. The resulting TLS session provides an encrypted tunnel to protect subsequent communications.

2.  **Authenticate the client securely inside the encrypted tunnel.** After the tunnel is established, a second method (such as MSCHAPv2 or another TLS handshake) allows the server to authenticate the client via the client’s credentials (such as an MSCHAPv2 username and password or a TLS certificate and private key). This client authentication is protected by the encrypted tunnel.

Upon successful authentication, the client and server generate a Pairwise Master Key (PMK). This is used to establish a secure Wi-Fi association between the STA and the Access Point.

##### Supported WPA Enterprise methods

To maximise compatibility with a broad range of Enterprise networks, WINCS02 supports the following tunnel and credential methods:

<table>
<tbody>
<tr>
<td><strong>Method</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr>
<td><strong>EAP-TTLSv0/MSCHAPv2</strong></td>
<td>TLS tunnel method is TTLSv0; client authentication is done using MSCHAPv2</td>
</tr>
<tr>
<td><strong>EAP-PEAPv0/MSCHAPv2</strong></td>
<td>TLS tunnel method is PEAPv0; client authentication method is MSCHAPv2</td>
</tr>
<tr>
<td><strong>EAP-PEAPv1/MSCHAPv2</strong></td>
<td>TLS tunnel method is PEAPv1; client authentication method is MSCHAPv2</td>
</tr>
<tr>
<td><strong>EAP-TLS</strong></td>
<td>Single-step process with mutual authentication in the TLS handshake</td>
</tr>
<tr>
<td><strong>EAP-PEAPv0/TLS</strong></td>
<td>TLS tunnel method is PEAPv0; client authentication method is another TLS handshake</td>
</tr>
<tr>
<td><strong>EAP-PEAPv1/TLS</strong></td>
<td>TLS tunnel method is PEAPv1; client authentication method is another TLS handshake</td>
</tr>
</tbody>
</table>

---
##### Configuring WPA Enterprise methods and security credentials

In order to use WPA Enterprise to connect the STA to an AP, via an authentication server, the following parameters must be set:

- The AP’s network name (SSID): [SSID](#AN_FUNC_WSTAC_STORE_ID_SSID)

- The security type (WPA Enterprise): [SEC_TYPE](#AN_FUNC_WSTAC_STORE_ID_SEC_TYPE)

- The unprotected user identity (many servers accept an anonymous identity): [ENT_IDENT_PLAIN](#AN_FUNC_WSTAC_STORE_ID_ENT_IDENT_PLAIN)

- The protected user identity: [ENT_IDENT_PROT](#AN_FUNC_WSTAC_STORE_ID_ENT_IDENT_PROT)

> [!NOTE]
> The protected user identity parameter may be left unset if the tunnel method parameter is set to "None" or "TTLSv0".

- The client credential type (TLS or MSCHAPv2): [ENT_CRED_TYPE](#AN_FUNC_WSTAC_STORE_ID_ENT_CRED_TYPE)

- The TLS configuration index for the tunnel method: [ENT_TUNN_TLS_CONF](#AN_FUNC_WSTAC_STORE_ID_ENT_TUNN_TLS_CONF)

> [!NOTE]
> The TLS configuration index for the tunnel method may be left unset if the tunnel method parameter is set to "None".

In addition:

- If the client credential type is TLS, the TLS configuration index to use for client credentials must be set: [ENT_CRED_TLS_CONF](#AN_FUNC_WSTAC_STORE_ID_ENT_CRED_TLS_CONF)

- If the client credential type is MSCHAPv2, the MSCHAPv2 username and password parameters must be set: [ENT_MSCHV2_UN](#AN_FUNC_WSTAC_STORE_ID_ENT_MSCHV2_UN) and [ENT_MSCHV2_PW](#AN_FUNC_WSTAC_STORE_ID_ENT_MSCHV2_PW)

Other WPA Enterprise credentials are optional, with default behaviours if they are not set:

- The WPA Enterprise tunnel method (TTLSv0, PEAPv0, PEAPv1, "none" or "any"; defaults to "any"): [ENT_TUNN_METHOD](#AN_FUNC_WSTAC_STORE_ID_ENT_TUNN_METHOD)

> [!NOTE]
> TLS configurations must be configured using the [TLSC](#AN_MOD_TLS) module. In particular:
>
> - If the TLS configuration is to be used for client credentials, the client’s certificate and private key must be specified via [CERT_NAME](#AN_FUNC_TLSC_STORE_ID_CERT_NAME) and [PRI_KEY_NAME](#AN_FUNC_TLSC_STORE_ID_PRI_KEY_NAME)
>
> - For EAP-PEAPv0 tunnel method, TLS session caching is not supported and [SESSION_CACHING](#AN_FUNC_TLSC_STORE_ID_SESSION_CACHING) is ignored
>
> - For TLS credential method, TLS session caching is not used and [SESSION_CACHING](#AN_FUNC_TLSC_STORE_ID_SESSION_CACHING) is ignored
>
> - For WPA3 (and WPA2/WPA3 transition mode) Enterprise, server domain name verification must be enabled via [PEER_DOMAIN_VERIFY](#AN_FUNC_TLSC_STORE_ID_PEER_DOMAIN_VERIFY) and [DOMAIN_NAME](#AN_FUNC_TLSC_STORE_ID_DOMAIN_NAME)

> [!NOTE]
> For EAP-PEAP/TLS methods, it may be appropriate and convenient to use the same TLS configuration for both the tunnel method and the client credentials.

---
##### Example WPA Enterprise Configurations

###### Example 1: WPA3 Enterprise with MSCHAPv2 credentials

First configure a TLS context for establishing a secure encrypted tunnel:

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify file name of CA certificate
    APP->>API: WINC_CmdTLSC(1,1,"radius_cert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify authentication server's domain name
    APP->>API: WINC_CmdTLSC(1,6,"wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Query to ensure time is valid (knowledge of current time is needed for TLS)
    APP->>API: WINC_CmdTIME(3)
    API->>APP: Status:WINC_CMD_ID_TIME(OK)
    API->>APP: AEC:WINC_AEC_ID_TIME("2025-10-24T18:03:43.00Z")
```

Then configure the STA connection parameters, making use of the above TLS context:

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify SSID of Access Point
    APP->>API: WINC_CmdWSTAC(1,"AUTO-WPA3-ENTERPRISE")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set security type to WPA3-Enterprise
    APP->>API: WINC_CmdWSTAC(2,9)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set Enterprise identity, to be sent unprotected (anonymous username)
    APP->>API: WINC_CmdWSTAC(20,"Anonymous@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set Enterprise identity, to be sent protected inside secure tunnel (real username)
    APP->>API: WINC_CmdWSTAC(21,"my_username@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set TLSC config index to use for establishing the tunnel
    APP->>API: WINC_CmdWSTAC(26,1)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set credential type to MSCHAPv2
    APP->>API: WINC_CmdWSTAC(30,1)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set MSCHAPv2 username
    APP->>API: WINC_CmdWSTAC(32,"my_username")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set MSCHAPv2 password
    APP->>API: WINC_CmdWSTAC(33,"my_password")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
```

Note that the tunnel method has not been specified here. Either EAP-TTLS or EAP-PEAP may be used, depending on the server’s request.

Now connect:

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Enable DHCP client
    APP->>API: WINC_CmdNETIFC(0,10,1)
    API->>APP: Status:WINC_CMD_ID_NETIFC(OK)
    Note right of APP: Start connection attempt
    APP->>API: WINC_CmdWSTA(1)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note left of API: Link up: connected on channel 6 to an AP with BSSID 00:01:02:03:04:05
    API->>APP: AEC:WINC_AEC_ID_WSTALU(1,"00:01:02:03:04:05",6)
    Note left of API: IP address received via auto configuration (DHCP/SLAAC)
    API->>APP: AEC:WINC_AEC_ID_WSTAAIP(1,"192.168.0.20")
```

---
###### Example 2: WPA3 Enterprise with EAP-PEAPv1/TLS method

First configure a TLS context, including the user’s certificate and private key:

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify file name of CA certificate
    APP->>API: WINC_CmdTLSC(2,1,"radius_cert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of user's certificate
    APP->>API: WINC_CmdTLSC(2,2,"my_cert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of user's private key
    APP->>API: WINC_CmdTLSC(2,3,"my_key")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify authentication server's domain name
    APP->>API: WINC_CmdTLSC(2,6,"wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Query to ensure time is valid (knowledge of current time is needed for TLS)
    APP->>API: WINC_CmdTIME(3)
    API->>APP: Status:WINC_CMD_ID_TIME(OK)
    API->>APP: AEC:WINC_AEC_ID_TIME("2025-10-24T18:03:43.00Z")
```

Then configure the STA connection parameters, making use of the above TLS context for both establishing the tunnel and authenticating the client:

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify SSID of Access Point
    APP->>API: WINC_CmdWSTAC(1,"AUTO-WPA3-ENTERPRISE")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set security type to WPA3-Enterprise
    APP->>API: WINC_CmdWSTAC(2,9)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set EAP identity to use during tunnel establishment (anonymous username)
    APP->>API: WINC_CmdWSTAC(20,"Anonymous@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set EAP identity to use inside secure tunnel (real username)
    APP->>API: WINC_CmdWSTAC(21,"my_username@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Restrict tunnel method to PEAPv1
    APP->>API: WINC_CmdWSTAC(25,4)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set TLSC config index to use for establishing the tunnel
    APP->>API: WINC_CmdWSTAC(26,2)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set credential type to TLS
    APP->>API: WINC_CmdWSTAC(30,0)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set TLSC config index to use for authenticating the client
    APP->>API: WINC_CmdWSTAC(31,2)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
```

Now connect:

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Enable DHCP client
    APP->>API: WINC_CmdNETIFC(0,10,1)
    API->>APP: Status:WINC_CMD_ID_NETIFC(OK)
    Note right of APP: Start connection attempt
    APP->>API: WINC_CmdWSTA(1)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note left of API: Link up: connected on channel 6 to an AP with BSSID 00:01:02:03:04:05
    API->>APP: AEC:WINC_AEC_ID_WSTALU(1,"00:01:02:03:04:05",6)
    Note left of API: IP address received via auto configuration (DHCP/SLAAC)
    API->>APP: AEC:WINC_AEC_ID_WSTAAIP(1,"192.168.0.20")
```

---
### Function Reference:

<a id="AN_FUNC_AT_WSTA_WSTAC"></a>
#### WINC_CmdWSTAC

##### Description

This function is used to read or set the WINC’s Wi-Fi station mode configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdWSTAC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDWSTAC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_WSTA_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_SSID"></span> 1</p></td>
<td style="text-align: left;"><p>SSID</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Network name<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_SEC_TYPE"></span> 2</p></td>
<td style="text-align: left;"><p>SEC_TYPE</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Security type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OPEN</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2_PERS_MIXED</p></td>
<td style="text-align: left;"><p>WPA2-Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2_PERS</p></td>
<td style="text-align: left;"><p>WPA2-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3_PERS_TRANS</p></td>
<td style="text-align: left;"><p>WPA3-Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3_PERS</p></td>
<td style="text-align: left;"><p>WPA3-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>WPA2_ENT_MIXED</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>WPA2_ENT</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>WPA3_ENT_TRANS</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>WPA3_ENT</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_CREDENTIALS"></span> 3</p></td>
<td style="text-align: left;"><p>CREDENTIALS</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Credentials for connecting to the network<br />
Maximum length of string is 128<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_CHANNEL"></span> 4</p></td>
<td style="text-align: left;"><p>CHANNEL</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Current channel of BSS (or 0 for any)<br />
<br />
Valid range is 0 to 13<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_BSSID"></span> 5</p></td>
<td style="text-align: left;"><p>BSSID</p></td>
<td style="text-align: left;"><p>MACADDR<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of the network to connect to<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_CONN_TIMEOUT"></span> 7</p></td>
<td style="text-align: left;"><p>CONN_TIMEOUT</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Connection timeout in milliseconds<br />
<br />
Valid range is 0 to 0x7FFFFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>NETIF_IDX</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Network interface index<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ROAMING"></span> 9</p></td>
<td style="text-align: left;"><p>ROAMING</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Roaming state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Roaming is disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>WIFI</p></td>
<td style="text-align: left;"><p>Roaming is enabled on WiFi only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>LAYER3</p></td>
<td style="text-align: left;"><p>Roaming is enabled on layer 3.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_IDENT_PLAIN"></span> 20</p></td>
<td style="text-align: left;"><p>ENT_IDENT_PLAIN</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Identity for Enterprise, to be sent unprotected<br />
Maximum length of string is 255<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_IDENT_PROT"></span> 21</p></td>
<td style="text-align: left;"><p>ENT_IDENT_PROT</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Identity for Enterprise, to be sent protected (PEAP tunnels only)<br />
Maximum length of string is 255<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_TUNN_METHOD"></span> 25</p></td>
<td style="text-align: left;"><p>ENT_TUNN_METHOD</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Tunnel method for Enterprise<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>ANY</p></td>
<td style="text-align: left;"><p>Any.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>NONE</p></td>
<td style="text-align: left;"><p>None.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>TTLSV0</p></td>
<td style="text-align: left;"><p>TTLSv0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>PEAPV0</p></td>
<td style="text-align: left;"><p>PEAPv0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>PEAPV1</p></td>
<td style="text-align: left;"><p>PEAPv1.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_TUNN_TLS_CONF"></span> 26</p></td>
<td style="text-align: left;"><p>ENT_TUNN_TLS_CONF</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC) to use for Enterprise tunnel<br />
<br />
Valid range is 0 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_CRED_TYPE"></span> 30</p></td>
<td style="text-align: left;"><p>ENT_CRED_TYPE</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Type of credentials for Enterprise<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>TLS</p></td>
<td style="text-align: left;"><p>TLS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>MSCHAPV2</p></td>
<td style="text-align: left;"><p>MSCHAPv2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_CRED_TLS_CONF"></span> 31</p></td>
<td style="text-align: left;"><p>ENT_CRED_TLS_CONF</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC) to use for Enterprise TLS credentials<br />
<br />
Valid range is 0 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_MSCHV2_UN"></span> 32</p></td>
<td style="text-align: left;"><p>ENT_MSCHV2_UN</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Username element of Enterprise MSCHAPv2 credentials<br />
Maximum length of string is 255<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_ENT_MSCHV2_PW"></span> 33</p></td>
<td style="text-align: left;"><p>ENT_MSCHV2_PW</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Password element of Enterprise MSCHAPv2 credentials<br />
Maximum length of string is 255<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_MFP_TYPE"></span> 50</p></td>
<td style="text-align: left;"><p>MFP_TYPE</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Management Frame Protection configuration<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>MFP Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>MFP Enabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>REQUIRED</p></td>
<td style="text-align: left;"><p>MFP Required.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_FUNC_WSTAC_STORE_ID_WPA3_TD"></span> 51</p></td>
<td style="text-align: left;"><p>WPA3_TD</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>WPA3 Transition disable modifier<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>MODIFIED</p></td>
<td style="text-align: left;"><p>WPA3 Transition algorithms not modified.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>WPA3 Transition algorithms are disabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_WSTA_WSTA"></a>
#### WINC_CmdWSTA

##### Description

This function is used to control or query the WINC’s station mode functionality.

    bool WINC_CmdWSTA
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optState
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optState</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>State of the Wi-Fi station feature.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLE</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLE</p></td>
<td style="text-align: left;"><p>Use configuration from WINC_CmdWSTAC.</p></td>
</tr>
</tbody>
</table>
<p>optState will be ignored if its value is<br />
WINC_CMDWSTA_STATE_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response               | Description |
|------------------------|-------------|
| \<ASSOC_ID\>,\<STATE\> | State       |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Connected state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NOT_CONNECTED</p></td>
<td style="text-align: left;"><p>Not connected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CONNECTED</p></td>
<td style="text-align: left;"><p>Connected.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_WSTA_WSTAAIP"></a>
#### WINC_AEC_ID_WSTAAIP

##### Description

**Indication of STA automatic address assignment.**

| AEC                         | Description                             |
|-----------------------------|-----------------------------------------|
| \<ASSOC_ID\>,\<IP_ADDRESS\> | Assignment of IP address to association |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;IP_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>IP address assigned<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_WSTA_WSTALD"></a>
#### WINC_AEC_ID_WSTALD

##### Description

**Link lost.**

| AEC          | Description |
|--------------|-------------|
| \<ASSOC_ID\> | Link down   |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_WSTAERR

##### Description

**Connection error.**

| AEC            | Description |
|----------------|-------------|
| \<ERROR_CODE\> | Link error  |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_WSTA_WSTALU"></a>
#### WINC_AEC_ID_WSTALU

##### Description

**Link established.**

| AEC                                | Description |
|------------------------------------|-------------|
| \<ASSOC_ID\>,\<BSSID\>,\<CHANNEL\> | Link up     |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BSSID&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of the Access Point the DCE has connected to<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CHANNEL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The channel number of network<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_WSTA_WSTAROAM"></a>
#### WINC_AEC_ID_WSTAROAM

##### Description

**Roaming occurred.**

| AEC          | Description      |
|--------------|------------------|
| \<ASSOC_ID\> | Roaming occurred |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_WSTA_PERSONAL"></a>
**WPA Personal: Configure STA connection parameters**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify SSID of Access Point
    APP->>API: WINC_CmdWSTAC(1,"MyAP")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set security type to WPA2-Personal
    APP->>API: WINC_CmdWSTAC(2,3)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set WPA2 Personal passphrase for connecting to the Access Point
    APP->>API: WINC_CmdWSTAC(3,"MyAPPSK")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
```

<a id="EXAMPLE_WSTA_CONNECT"></a>
**Connect at Wi-Fi and IP layers**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Enable DHCP client
    APP->>API: WINC_CmdNETIFC(0,10,1)
    API->>APP: Status:WINC_CMD_ID_NETIFC(OK)
    Note right of APP: Start connection attempt
    APP->>API: WINC_CmdWSTA(1)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note left of API: Link up: connected on channel 6 to an AP with BSSID 00:01:02:03:04:05
    API->>APP: AEC:WINC_AEC_ID_WSTALU(1,"00:01:02:03:04:05",6)
    Note left of API: IP address received via auto configuration (DHCP/SLAAC)
    API->>APP: AEC:WINC_AEC_ID_WSTAAIP(1,"192.168.0.20")
```

<a id="EXAMPLE_WSTA_RECONNECT"></a>
**Some disconnections, reconnections and roaming**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Start connection attempt
    APP->>API: WINC_CmdWSTA(1)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note left of API: Link up: connected on channel 11
    API->>APP: AEC:WINC_AEC_ID_WSTALU(1,"00:01:02:03:04:05",11)
    Note left of API: IP address received via auto configuration (DHCP/SLAAC)
    API->>APP: AEC:WINC_AEC_ID_WSTAAIP(1,"192.168.0.20")
    Note right of APP: Disconnect
    APP->>API: WINC_CmdWSTA(0)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note right of APP: Query STA status
    APP->>API: WINC_CmdWSTA()
    Note left of API: STA is not connected
    API->>APP: Response:WINC_CMD_ID_WSTA(0)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note right of APP: Start connection attempt
    APP->>API: WINC_CmdWSTA(1)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note left of API: Link up: connected on channel 11
    API->>APP: AEC:WINC_AEC_ID_WSTALU(1,"00:01:02:03:04:05",11)
    Note left of API: IP address received via auto configuration (DHCP/SLAAC)
    API->>APP: AEC:WINC_AEC_ID_WSTAAIP(1,"192.168.0.20")
    Note left of API: STA has roamed
    API->>APP: AEC:WINC_AEC_ID_WSTAROAM(1)
    Note left of API: Change in IP address due to layer 3 roaming
    API->>APP: AEC:WINC_AEC_ID_WSTAAIP(1,"10.1.0.5")
    Note right of APP: Query STA status
    APP->>API: WINC_CmdWSTA()
    Note left of API: STA is connected
    API->>APP: Response:WINC_CMD_ID_WSTA(1)
    API->>APP: Status:WINC_CMD_ID_WSTA(OK)
    Note left of API: Link down
    API->>APP: AEC:WINC_AEC_ID_WSTALD()
```

<a id="EXAMPLE_WSTA_ENTERPRISE_TUNNEL"></a>
**WPA Enterprise: Configure a TLS context for establishing a tunnel**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify file name of CA certificate
    APP->>API: WINC_CmdTLSC(1,1,"radius_cert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify authentication server's domain name
    APP->>API: WINC_CmdTLSC(1,6,"wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Query to ensure time is valid (knowledge of current time is needed for TLS)
    APP->>API: WINC_CmdTIME(3)
    API->>APP: Status:WINC_CMD_ID_TIME(OK)
    API->>APP: AEC:WINC_AEC_ID_TIME("2025-10-24T18:03:43.00Z")
```

<a id="EXAMPLE_WSTA_ENTERPRISE_MSCHAPV2"></a>
**WPA Enterprise: Configure STA connection parameters for MSCHAPv2**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify SSID of Access Point
    APP->>API: WINC_CmdWSTAC(1,"AUTO-WPA3-ENTERPRISE")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set security type to WPA3-Enterprise
    APP->>API: WINC_CmdWSTAC(2,9)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set Enterprise identity, to be sent unprotected (anonymous username)
    APP->>API: WINC_CmdWSTAC(20,"Anonymous@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set Enterprise identity, to be sent protected inside secure tunnel (real username)
    APP->>API: WINC_CmdWSTAC(21,"my_username@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set TLSC config index to use for establishing the tunnel
    APP->>API: WINC_CmdWSTAC(26,1)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set credential type to MSCHAPv2
    APP->>API: WINC_CmdWSTAC(30,1)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set MSCHAPv2 username
    APP->>API: WINC_CmdWSTAC(32,"my_username")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set MSCHAPv2 password
    APP->>API: WINC_CmdWSTAC(33,"my_password")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
```

<a id="EXAMPLE_WSTA_ENTERPRISE_TLS_TLSC"></a>
**WPA Enterprise: Configure a TLS context for EAP-PEAPv1/TLS**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify file name of CA certificate
    APP->>API: WINC_CmdTLSC(2,1,"radius_cert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of user's certificate
    APP->>API: WINC_CmdTLSC(2,2,"my_cert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of user's private key
    APP->>API: WINC_CmdTLSC(2,3,"my_key")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify authentication server's domain name
    APP->>API: WINC_CmdTLSC(2,6,"wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Query to ensure time is valid (knowledge of current time is needed for TLS)
    APP->>API: WINC_CmdTIME(3)
    API->>APP: Status:WINC_CMD_ID_TIME(OK)
    API->>APP: AEC:WINC_AEC_ID_TIME("2025-10-24T18:03:43.00Z")
```

<a id="EXAMPLE_WSTA_ENTERPRISE_TLS_WSTAC"></a>
**WPA Enterprise: Configure STA connection parameters for EAP-PEAPv1/TLS**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Specify SSID of Access Point
    APP->>API: WINC_CmdWSTAC(1,"AUTO-WPA3-ENTERPRISE")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set security type to WPA3-Enterprise
    APP->>API: WINC_CmdWSTAC(2,9)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set EAP identity to use during tunnel establishment (anonymous username)
    APP->>API: WINC_CmdWSTAC(20,"Anonymous@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set EAP identity to use inside secure tunnel (real username)
    APP->>API: WINC_CmdWSTAC(21,"my_username@wifi.alpha.net")
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Restrict tunnel method to PEAPv1
    APP->>API: WINC_CmdWSTAC(25,4)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set TLSC config index to use for establishing the tunnel
    APP->>API: WINC_CmdWSTAC(26,2)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set credential type to TLS
    APP->>API: WINC_CmdWSTAC(30,0)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
    Note right of APP: Set TLSC config index to use for authenticating the client
    APP->>API: WINC_CmdWSTAC(31,2)
    API->>APP: Status:WINC_CMD_ID_WSTAC(OK)
```

---
<a id="AN_MOD_ASSOC"></a>
## ASSOC (Module ID = 22)

### Function Reference:

#### WINC_CmdASSOC

##### Description

This function is used to query current WiFi associations.

    bool WINC_CmdASSOC
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t optAssocId
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optAssocId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>Association ID.<br />
</p>
<p>optAssocId will be ignored if its value is<br />
WINC_CMDASSOC_ASSOC_ID_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_ASSOC

##### Description

**WiFi association report.**

| AEC                                        | Description             |
|--------------------------------------------|-------------------------|
| \<ASSOC_ID\>,\<AP_STA\>,\<BSSID\>,\<RSSI\> | WiFi association report |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;AP_STA&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>AP or STA<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>AP</p></td>
<td style="text-align: left;"><p>AP.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>STA</p></td>
<td style="text-align: left;"><p>STA.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BSSID&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of association peer<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSSI&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>RSSI<br />
</p></td>
</tr>
</tbody>
</table>

---
## SI (Module ID = 23)

### Function Reference:

#### WINC_CmdSI

##### Description

This function is used to query system information.

    bool WINC_CmdSI
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t optFilter
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optFilter</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>System information filter bitmask.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0x01</p></td>
<td style="text-align: left;"><p>WIFI_MEM_ALLOC</p></td>
<td style="text-align: left;"><p>WiFi memory allocation stats.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x02</p></td>
<td style="text-align: left;"><p>WIFI_PKTS</p></td>
<td style="text-align: left;"><p>WiFi packet stats.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x04</p></td>
<td style="text-align: left;"><p>HEAP_ALLOC</p></td>
<td style="text-align: left;"><p>Heap allocation stats.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x08</p></td>
<td style="text-align: left;"><p>STACK_USAGE</p></td>
<td style="text-align: left;"><p>Stack usage stats.</p></td>
</tr>
</tbody>
</table>
<p>optFilter will be ignored if its value is<br />
WINC_CMDSI_FILTER_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response   | Description |
|------------|-------------|
| \<UPTIME\> | Response    |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;UPTIME&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>System uptime in seconds<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_SIMSTAT

##### Description

**WiFi memory statistics for each type of memory pool.**

| AEC | Description |
|----|----|
| \<TYPE\>,\<ALLOC\>,\<FREE\>,\<ALLOC_SZ\>,\<FREE_SZ\> | WiFi memory statistic |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>MEM</p></td>
<td style="text-align: left;"><p>Memory.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CFG</p></td>
<td style="text-align: left;"><p>Config.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>HPTX</p></td>
<td style="text-align: left;"><p>High priority TX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>HPRX</p></td>
<td style="text-align: left;"><p>High priority RX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>NRMTX</p></td>
<td style="text-align: left;"><p>Normal priority TX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>NRMRX</p></td>
<td style="text-align: left;"><p>Normal priority RX.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of memory allocations made<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of memory frees<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC_SZ&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Total bytes allocated<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_SZ&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Total bytes freed<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SIMERR

##### Description

**WiFi Memory errors.**

| AEC           | Description        |
|---------------|--------------------|
| \<ALLOC_ERR\> | WiFi memory errors |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC_ERR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Memory allocation errors<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SIWPKTS

##### Description

**WiFi packets statistics.**

| AEC           | Description  |
|---------------|--------------|
| \<TX\>,\<RX\> | WiFi packets |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TX&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>WiFi packets transmitted<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RX&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>WiFi packets received<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SIHEAP

##### Description

**Heap allocation statistics.**

| AEC | Description |
|----|----|
| \<ALLOC\>,\<FREE\>,\<ALLOC_SZ\>,\<FREE_SZ\>,\<PEAK_ALLOC_SZ\> | Heap statistics |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of memory allocations made<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of memory frees<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC_SZ&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Total bytes allocated<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_SZ&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Total bytes freed<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEAK_ALLOC_SZ&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Peak bytes allocated<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SIHERR

##### Description

**Heap allocation errors.**

| AEC           | Description |
|---------------|-------------|
| \<ALLOC_ERR\> | Heap errors |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC_ERR&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Memory allocation errors<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_SISTACK

##### Description

**Stack usage.**

| AEC | Description |
|----|----|
| \<STACK_MIN_RESERVED\>,\<STACK_RESERVED\>,\<STACK_USAGE\> | Stack statistics |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;STACK_MIN_RESERVED&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Minimum stack reserved memory<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;STACK_RESERVED&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Stack reserved memory<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;STACK_USAGE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Stack usage<br />
</p></td>
</tr>
</tbody>
</table>

---
## WPROV (Module ID = 25)

### Function Reference:

#### WINC_CmdWPROVC

##### Description

This function is used to read or set the provisioning service configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdWPROVC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDWPROVC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_WPROV_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PORT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Service listening port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>ASCII</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>ASCII or binary protocol<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>BINARY</p></td>
<td style="text-align: left;"><p>Binary protocol.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ASCII</p></td>
<td style="text-align: left;"><p>ASCII protocol.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>PROTOCOL_VERSION</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>IP protocol version<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>IPV4</p></td>
<td style="text-align: left;"><p>IPv4.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>IPV6</p></td>
<td style="text-align: left;"><p>IPv6.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdWPROV

##### Description

This function is used to control or query the provisioning service.

    bool WINC_CmdWPROV
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optState
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optState</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>State of the provisioning service.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLE</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLE</p></td>
<td style="text-align: left;"><p>Use configuration from WINC_CmdWPROVC.</p></td>
</tr>
</tbody>
</table>
<p>optState will be ignored if its value is<br />
WINC_CMDWPROV_STATE_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_WPROVAT

##### Description

**Indication of client attach to provisioning service.**

| AEC | Description |
|----|----|
| \<ID\>,\<IP_ADDRESS\>,\<PORT\> | Attachment of client to provisioning service |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Client ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;IP_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>IP address assigned<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PORT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Port<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_WPROVDT

##### Description

**Indication of client detach from provisioning service.**

| AEC    | Description                                    |
|--------|------------------------------------------------|
| \<ID\> | Detachment of client from provisioning service |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Client ID<br />
</p></td>
</tr>
</tbody>
</table>

---
## DI (Module ID = 26)

### Function Reference:

<a id="AN_FUNC_AT_DI_DI"></a>
#### WINC_CmdDI

##### Description

This function is used to query the device information.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdDI
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDDI_ID_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_DI_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>DEVICE_ID</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Device ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>NUM_IMAGES</p></td>
<td style="text-align: left;"><p>INTEGER<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Number of images<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>IMAGE_INFO</p></td>
<td style="text-align: left;"><p>Complex Value<sup>1</sup><br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Image information<br />
This is a multiple value parameter<br />
with an ID range 15.0 to 15.1<br />
</p></td>
</tr>
</tbody>
</table>

| No. | Complex Value                                      | Description       |
|-----|----------------------------------------------------|-------------------|
| 1   | \<SEQ_NUM\>,\<VERSION\>,\<SRC_ADDR\>,\<IMG_STATE\> | Image information |

**Complex Value Syntax**

<table>
<caption>Complex Value Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SEQ_NUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Sequence number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VERSION&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Version information<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SRC_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Source address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;IMG_STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Image state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>LATENT</p></td>
<td style="text-align: left;"><p>The image has not yet been activated.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ACTIVATED</p></td>
<td style="text-align: left;"><p>The image will run on next boot (subject to verification).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>CURRENT</p></td>
<td style="text-align: left;"><p>The image is currently running.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>ROLLBACK</p></td>
<td style="text-align: left;"><p>The image will run on next boot (subject to verification) if the current image is invalidated.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
---
### Examples:

<a id="EXAMPLE_b24cb7601966bd304010fa7449e5f57c0507b958"></a>
**Query device information with [WINC_CmdDI](#AN_FUNC_AT_DI_DI)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Query all device information
    APP->>API: WINC_CmdDI()
    Note left of API: Device ID
    API->>APP: Response:WINC_CMD_ID_DI(1,0x29C70053)
    Note left of API: 2 images
    API->>APP: Response:WINC_CMD_ID_DI(14,2)
    Note left of API: Image info for currently running image
    API->>APP: Response:WINC_CMD_ID_DI(15.0,0xFFEEDDC0,0x00010200,0x60000000,2)
    Note left of API: Image info for latent image
    API->>APP: Response:WINC_CMD_ID_DI(15.1,0xFFFFFFFF,0x00010300,0xFFFFFFFF,0)
    API->>APP: Status:WINC_CMD_ID_DI(OK)
```

---
<a id="AN_MOD_EXTCRYPTO"></a>
## EXTCRYPTO (Module ID = 27)

### Introduction

Cryptographic operations can be delegated to an external crypto device, providing secure key storage and hardware-accelerated public key operations. The user can choose the on-module ATECC608A-TNGTLS or equivalent third-party device.

The ATECC608A-TNGTLS is the Trust-and-Go pre-provisioned variant of the ATECC608, featuring ECDSA signing, ECC Private Key secure storage, and X.509 compressed certificate storage. Access to the on-module secure element is made through a separate I2C or SWI interface.

The [WINC_AEC_ID_EXTCRYPTO](#AN_AEC_AT_EXTCRYPTO_EXTCRYPTO) AEC allows the application to receive a crypto operation request from the WINCS02. The [WINC_CmdEXTCRYPTO](#AN_FUNC_AT_EXTCRYPTO_EXTCRYPTO) function is used to send the operation result back to the WINCS02.

Crypto operation requests are enabled via the [EXTCRYPTO_OPS](#AN_FUNC_TLSC_STORE_ID_EXTCRYPTO_OPS) parameter of the [WINC_CmdTLSC](#AN_FUNC_AT_TLS_TLSC) function. The only supported operation is ECDSA signing.

#### Using External Crypto for Secure Signing

To leverage the crypto device for secure signing, the application should follow these steps:

1.  Retrieve from the crypto device the X.509 certificate that includes the public key corresponding to the securely stored private key.

2.  Send the X.509 certificate to the WINCS02 using the [WINC_CmdFSSTORE](#AN_FUNC_AT_FS_FLFS_FSSTORE) function.

3.  Enable secure signing via the external crypto device and specify the certificate in the TLS configuration.

    See example [configuring TLS with external crypto](#EXAMPLE_EXTCRYPTO_TLS).

4.  Respond to signing requests from the [WINC_AEC_ID_EXTCRYPTO](#AN_AEC_AT_EXTCRYPTO_EXTCRYPTO) AEC with the [WINC_CmdEXTCRYPTO](#AN_FUNC_AT_EXTCRYPTO_EXTCRYPTO) function.

    See example [handling signing request and calling response function](#EXAMPLE_EXTCRYPTO).

> [!NOTE]
> The ECC curve used for signing is selected according to the certificate public key. Refer to the CURVE element in the [WINC_AEC_ID_EXTCRYPTO](#AN_AEC_AT_EXTCRYPTO_EXTCRYPTO) AEC for the list of supported curves.

> [!NOTE]
> The application code is responsible for interacting with the external crypto device to retrieve the certificate and forward signing requests and responses.

---
### Function Reference:

<a id="AN_FUNC_AT_EXTCRYPTO_EXTCRYPTO"></a>
#### WINC_CmdEXTCRYPTO

##### Description

This function is used to provide the result of an external crypto operation.

    bool WINC_CmdEXTCRYPTO
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t opId
        uint8_t status
        const uint8_t* pOptSignature
        size_t lenOptSignature
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>opId</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>Operation identifier, matching &lt;OP_ID&gt; in corresponding AEC.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>status</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Operation success or failure.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>SUCCESS</p></td>
<td style="text-align: left;"><p>Operation succeeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>FAILURE</p></td>
<td style="text-align: left;"><p>Operation failed.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>pOptSignature</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Signature (big endian). For ECDSA signatures: R then S, each the size of the curve..<br />
</p>
<p>pOptSignature will be ignored if its value is NULL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptSignature</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pOptSignature.<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_EXTCRYPTO_EXTCRYPTO"></a>
#### WINC_AEC_ID_EXTCRYPTO

##### Description

**This event is used to request an external crypto operation.**

| AEC | Description |
|----|----|
| \<OP_ID\>,\<OP_TYPE\>,\<OP_SOURCE_TYPE\>,\<OP_SOURCE_ID\>,\<SIGN_TYPE\>,\<CURVE\>,\<SIGN_VALUE\> | Request an external signing operation |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OP_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Operation identifier, to be included in EXTCRYPTO CMD<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OP_TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The type of operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SIGN</p></td>
<td style="text-align: left;"><p>Signing.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OP_SOURCE_TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The type of source requesting the operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>TLSC</p></td>
<td style="text-align: left;"><p>A TLSC configuration.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OP_SOURCE_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The ID of the source requesting the operation<br />
<br />
Valid range is 1 to 2<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGN_TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The type of signing operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ECDSA</p></td>
<td style="text-align: left;"><p>ECDSA.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CURVE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The ECDSA curve<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SECP256R1</p></td>
<td style="text-align: left;"><p>Curve secp256r1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>SECP384R1</p></td>
<td style="text-align: left;"><p>Curve secp384r1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>SECP521R1</p></td>
<td style="text-align: left;"><p>Curve secp521r1.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGN_VALUE&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>The value to be signed (big endian)<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_EXTCRYPTO_TLS"></a>
**Example of TLS configuration for secure signing via external crypto operations**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Enable server domain verification
    APP->>API: WINC_CmdTLSC(2,41,1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify server domain name
    APP->>API: WINC_CmdTLSC(2,6,"ServerDomain")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Enable server authentication
    APP->>API: WINC_CmdTLSC(2,40,1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of CA certificate
    APP->>API: WINC_CmdTLSC(2,1,"ServerRootCACert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Specify file name of ECC client certificate
    APP->>API: WINC_CmdTLSC(2,2,"EccClientCert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Enable signing via external crypto
    APP->>API: WINC_CmdTLSC(2,20,1)
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
```

<a id="EXAMPLE_EXTCRYPTO"></a>
**Example of signing request/response using [WINC_CmdEXTCRYPTO](#AN_FUNC_AT_EXTCRYPTO_EXTCRYPTO)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note left of API: Crypto request ID 123: ECDSA signing using curve secp256r1, for TLS config 2
    API->>APP: AEC:WINC_AEC_ID_EXTCRYPTO(123,1,1,2,1,1,[0123...cdef])
    Note right of APP: Response to crypto request ID 123
    APP->>API: WINC_CmdEXTCRYPTO(123,0,[0123...cdef])
    API->>APP: Status:WINC_CMD_ID_EXTCRYPTO(OK)
```

---
## WIFI (Module ID = 28)

### Function Reference:

<a id="AN_FUNC_AT_WIFI_WIFIC"></a>
#### WINC_CmdWIFIC

##### Description

This function is used to read or set the device’s Wi-Fi configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdWIFIC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDWIFIC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response       | Description   |
|----------------|---------------|
| \<ID\>,\<VAL\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_WIFI_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>REGDOMAIN_SELECTED</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Regulatory domain selected<br />
Maximum length of string is 6<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>REGDOMAIN_AVAILABLE</p></td>
<td style="text-align: left;"><p>STRING<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Regulatory domains available<br />
Maximum length of string is 6<br />
This is a multiple value parameter<br />
with an ID range 11.0 to 11.5<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>REGDOMAIN_CHANMASK24</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Regulatory channel mask (2.4 GHz)<br />
</p>
<table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: center;"><p><sup>15</sup><br />
-</p></td>
<td style="text-align: center;"><p><sup>14</sup><br />
-</p></td>
<td style="text-align: center;"><p><sup>13</sup><br />
CH14</p></td>
<td style="text-align: center;"><p><sup>12</sup><br />
CH13</p></td>
<td style="text-align: center;"><p><sup>11</sup><br />
CH12</p></td>
<td style="text-align: center;"><p><sup>10</sup><br />
CH11</p></td>
<td style="text-align: center;"><p><sup>9</sup><br />
CH1</p></td>
<td style="text-align: center;"><p><sup>8</sup><br />
CH9</p></td>
</tr>
<tr>
<td style="text-align: center;"><p><sup>7</sup><br />
CH8</p></td>
<td style="text-align: center;"><p><sup>6</sup><br />
CH7</p></td>
<td style="text-align: center;"><p><sup>5</sup><br />
CH6</p></td>
<td style="text-align: center;"><p><sup>4</sup><br />
CH5</p></td>
<td style="text-align: center;"><p><sup>3</sup><br />
CH4</p></td>
<td style="text-align: center;"><p><sup>2</sup><br />
CH3</p></td>
<td style="text-align: center;"><p><sup>1</sup><br />
CH2</p></td>
<td style="text-align: center;"><p><sup>0</sup><br />
CH1</p></td>
</tr>
</tbody>
</table>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0x0001</p></td>
<td style="text-align: left;"><p>CH1</p></td>
<td style="text-align: left;"><p>Channel 1 - 2412 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0002</p></td>
<td style="text-align: left;"><p>CH2</p></td>
<td style="text-align: left;"><p>Channel 2 - 2417 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0004</p></td>
<td style="text-align: left;"><p>CH3</p></td>
<td style="text-align: left;"><p>Channel 3 - 2422 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0008</p></td>
<td style="text-align: left;"><p>CH4</p></td>
<td style="text-align: left;"><p>Channel 4 - 2427 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0010</p></td>
<td style="text-align: left;"><p>CH5</p></td>
<td style="text-align: left;"><p>Channel 5 - 2432 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0020</p></td>
<td style="text-align: left;"><p>CH6</p></td>
<td style="text-align: left;"><p>Channel 6 - 2437 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0040</p></td>
<td style="text-align: left;"><p>CH7</p></td>
<td style="text-align: left;"><p>Channel 7 - 2442 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0080</p></td>
<td style="text-align: left;"><p>CH8</p></td>
<td style="text-align: left;"><p>Channel 8 - 2447 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0100</p></td>
<td style="text-align: left;"><p>CH9</p></td>
<td style="text-align: left;"><p>Channel 9 - 2452 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0200</p></td>
<td style="text-align: left;"><p>CH10</p></td>
<td style="text-align: left;"><p>Channel 10 - 2457 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0400</p></td>
<td style="text-align: left;"><p>CH11</p></td>
<td style="text-align: left;"><p>Channel 11 - 2462 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x0800</p></td>
<td style="text-align: left;"><p>CH12</p></td>
<td style="text-align: left;"><p>Channel 12 - 2467 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x1000</p></td>
<td style="text-align: left;"><p>CH13</p></td>
<td style="text-align: left;"><p>Channel 13 - 2472 MHz.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x2000</p></td>
<td style="text-align: left;"><p>CH14</p></td>
<td style="text-align: left;"><p>Channel 14 - 2485 MHz.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>POWERSAVE</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Power Save Mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OFF</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ON</p></td>
<td style="text-align: left;"><p>On.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>POWERSAVE_LISTEN_INTERVAL</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Listen Interval in units of beacon period<br />
<br />
Valid range is 3 to 100<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>POWERSAVE_INACT_LIMIT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Inactivity Time Limit - the sleep inactivity threshold/limit for power-save operation in seconds<br />
<br />
Valid range is 10 to 6000<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>30</p></td>
<td style="text-align: left;"><p>COEX_ENABLED</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>COEX_INTERFACE_TYPE</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter interface type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>3WIRE</p></td>
<td style="text-align: left;"><p>3-wire interface (BT_Act, BT_Prio, WLAN_Act).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>2WIRE</p></td>
<td style="text-align: left;"><p>2-wire interface (BT_Prio, WLAN_Act).</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>32</p></td>
<td style="text-align: left;"><p>COEX_WLAN_RX_VS_BT</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter WLAN Rx priority over BT Low Priority<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>WLAN_LOW</p></td>
<td style="text-align: left;"><p>WLAN Rx priority lower than BT Low Priority.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>WLAN_HIGH</p></td>
<td style="text-align: left;"><p>WLAN Rx priority higher than BT Low Priority.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>COEX_WLAN_TX_VS_BT</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter WLAN Tx priority over BT Low Priority<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>WLAN_LOW</p></td>
<td style="text-align: left;"><p>WLAN Tx priority lower than BT Low Priority.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>WLAN_HIGH</p></td>
<td style="text-align: left;"><p>WLAN Tx priority higher than BT Low Priority.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>COEX_ANTENNA_MODE</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter antenna mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEDICATED</p></td>
<td style="text-align: left;"><p>Dedicated antenna.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SHARED</p></td>
<td style="text-align: left;"><p>Shared antenna.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>AMPDU_TX_ENABLED</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Wi-Fi A-MPDU Tx Enable<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>TX_AMPDU_DISABLED</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>TX_AMPDU_ENABLED</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
---
### Examples:

<a id="EXAMPLE_83aadd2a5891271329d9dc62f4cea81d34571a9e"></a>
**Settings with [WINC_CmdWIFIC](#AN_FUNC_AT_WIFI_WIFIC)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Configure regulatory domain to USA
    APP->>API: WINC_CmdWIFIC(10,"USA")
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Configure regulatory domain to JPN
    APP->>API: WINC_CmdWIFIC(10,"JPN")
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Query regulatory domain
    APP->>API: WINC_CmdWIFIC(10)
    API->>APP: Response:WINC_CMD_ID_WIFIC(10,"JPN")
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Query power save mode
    APP->>API: WINC_CmdWIFIC(20)
    API->>APP: Response:WINC_CMD_ID_WIFIC(20,0)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Configure power save on
    APP->>API: WINC_CmdWIFIC(20,1)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
```

<a id="EXAMPLE_c37bae967b299185b054858a003c7507e0b388a9"></a>
**[WINC_CmdWIFIC](#AN_FUNC_AT_WIFI_WIFIC) coexistence settings for 3-wire PTA interface**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Configure 3-wire interface
    APP->>API: WINC_CmdWIFIC(31,0)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: WLAN RX priority higher than BT low priority
    APP->>API: WINC_CmdWIFIC(32,1)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: WLAN TX priority higher than BT low priority
    APP->>API: WINC_CmdWIFIC(33,1)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Shared antenna
    APP->>API: WINC_CmdWIFIC(34,1)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Enable coex
    APP->>API: WINC_CmdWIFIC(30,1)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
```

---
<a id="AN_MOD_NVM"></a>
## NVM (Module ID = 29)

### Function Reference:

#### WINC_CmdNVMC

##### Description

This function is used to read or set the NVM configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdNVMC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDNVMC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_NVM_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>START_OFFSET</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Starting address offset<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>NUM_SECTORS</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Number of sectors<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>SECTOR_SZ</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Sector size<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>CHECK_MODE</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Checking mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>CRC16</p></td>
<td style="text-align: left;"><p>CRC16.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdNVMER

##### Description

This function allows sector erase within the alternate firmware partition.

    bool WINC_CmdNVMER
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t sectorOffset
        uint8_t sectors
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sectorOffset</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Sector offset to be used for the NVM operation.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>sectors</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>The number of sectors to erase during NVM operation.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdNVMWR

##### Description

This function allows data to be written to the alternate firmware partition. Writes are performed as normal for flash devices, therefore it is recommended to erase the sector of data before performing a write. Write operations cannot cross a sector boundary.

    bool WINC_CmdNVMWR
    (
        WINC_CMD_REQ_HANDLE handle
        uint32_t offset
        uint16_t length
        const uint8_t* pData
        size_t lenData
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>offset</p></td>
<td style="text-align: left;"><p>uint32_t</p></td>
<td style="text-align: left;"><p>Byte offset to be used for the NVM operation.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The number of bytes for the NVM operation.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pData</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>The data to write in hexadecimal string format.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenData</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pData.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdNVMCHK

##### Description

This function allows checking of the alternate firmware partition.

    bool WINC_CmdNVMCHK
    (
        WINC_CMD_REQ_HANDLE handle
        uint32_t offset
        uint32_t length
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>offset</p></td>
<td style="text-align: left;"><p>uint32_t</p></td>
<td style="text-align: left;"><p>Byte offset to be used for the NVM operation.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>uint32_t</p></td>
<td style="text-align: left;"><p>The number of bytes for the NVM operation.<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdNVMRD

##### Description

This function allows reading of the alternate firmware partition.

    bool WINC_CmdNVMRD
    (
        WINC_CMD_REQ_HANDLE handle
        uint32_t offset
        uint16_t length
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>offset</p></td>
<td style="text-align: left;"><p>uint32_t</p></td>
<td style="text-align: left;"><p>Byte offset to be used for the NVM operation.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>The number of bytes for the NVM operation.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                       | Description   |
|--------------------------------|---------------|
| \<OFFSET\>,\<LENGTH\>,\<DATA\> | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OFFSET&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Byte offset<br />
<br />
Valid range is 0 to 0x000EFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes<br />
<br />
Valid range is 1 to 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Data bytes<br />
<br />
Valid range is 1 to 1024<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_NVMER

##### Description

**NVM Erase.**

| AEC         | Description       |
|-------------|-------------------|
|             | NVM erase success |
| No Elements |                   |

AEC Syntax

---
#### WINC_AEC_ID_NVMCHK

##### Description

**NVM Check.**

| AEC                                           | Description   |
|-----------------------------------------------|---------------|
| \<OFFSET\>,\<LENGTH\>,\<CHECK_MODE\>,\<HASH\> | Hash response |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OFFSET&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Byte offset<br />
<br />
Valid range is 0 to 0x000EFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes<br />
<br />
Valid range is 1 to 0x000F0000<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CHECK_MODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Checking mode used<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>CRC16</p></td>
<td style="text-align: left;"><p>CRC16.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;HASH&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Hash response<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_NVMERR

##### Description

**NVM error.**

| AEC            | Description |
|----------------|-------------|
| \<ERROR_CODE\> | NVM error   |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_NVM_EXAMPLE"></a>
**Simple example of NVM usage**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Erase first sector
    APP->>API: WINC_CmdNVMER(0,1)
    API->>APP: Status:WINC_CMD_ID_NVMER(OK)
    Note left of API: Erase complete AEC
    API->>APP: AEC:WINC_AEC_ID_NVMER()
    Note right of APP: Write 4 bytes of data to offset 0
    APP->>API: WINC_CmdNVMWR(0,4,[4D434850])
    API->>APP: Status:WINC_CMD_ID_NVMWR(OK)
    Note right of APP: Request CRC16 checksum, 4 bytes from offset 0
    APP->>API: WINC_CmdNVMCHK(0,4)
    API->>APP: Status:WINC_CMD_ID_NVMCHK(OK)
    Note left of API: CRC16 checksum AEC
    API->>APP: AEC:WINC_AEC_ID_NVMCHK(0x00000000,4,2,0xCD77)
    Note right of APP: Set check mode to SHA256
    APP->>API: WINC_CmdNVMC(4,11)
    API->>APP: Status:WINC_CMD_ID_NVMC(OK)
    Note right of APP: Request SHA256 hash, 4 bytes from offset 0
    APP->>API: WINC_CmdNVMCHK(0,4)
    API->>APP: Status:WINC_CMD_ID_NVMCHK(OK)
    Note left of API: SHA256 AEC
    API->>APP: AEC:WINC_AEC_ID_NVMCHK(0x00000000,4,11,[7BE8FA11F537A1CA4612D6E30CAF94A20F3C37999012119672BE21DAD2791D5C])
    Note right of APP: Read 4 bytes of data from offset 0
    APP->>API: WINC_CmdNVMRD(0,4)
    Note left of API: Read data response
    API->>APP: Response:WINC_CMD_ID_NVMRD(0x00000000,4,"MCHP")
    API->>APP: Status:WINC_CMD_ID_NVMRD(OK)
```

---
<a id="AN_MOD_DFU"></a>
## DFU (Module ID = 30)

### Introduction

Secure Device Firmware Update (DFU) is a process for upgrading the firmware of a secured device.

The WINCS02 device has non-volatile memory (NVM) with two partitions which may be used to store firmware images.

The partitions can be referred to as "low" and "high" based on their physical addresses. They can also be referred to as "current" and "alternate" based on their usage at a given time; in normal operation, the "current" partition contains a copy of the currently running firmware image, while the "alternate" partition may be blank or may contain a rollback image, a latent image or any other data.

The DFU process should involve the following steps:

1.  Determine the NVM partition in which to program the firmware image.

2.  Prepare the firmware image.

3.  Boot the device in DFU mode.

4.  Erase and program the NVM partition.

#### 1. Determine the NVM partition in which to program the firmware image

The appropriate NVM partition ("alternate", "current", "low" or "high") depends on the user’s upgrade policy. Two common upgrade policies are:

- A "flip-flop" policy in which the new firmware image is always programmed to the "alternate" partition.

- A "golden image" policy in which the initial firmware image is programmed to one partition (based on physical address), and subsequent firmware images are always programmed to the other partition.

#### 2. Prepare the firmware image

Locate the released WINCS02.bootable.dfu file for the firmware version to which you want to upgrade.

Read the firmware image from the file, then update two values:

- Sequence Number: The Sequence Number is the boot priority of the firmware image. Use the [WINC_CmdDFUSEQ](#AN_FUNC_AT_DFU_DFUSEQ) function to get the offset, length and value for updating it.

- Firmware Image Source Address: The Firmware Image Source Address must match the physical address of the NVM partition in which the firmware image is to be programmed. Use the [WINC_CmdDFUADR](#AN_FUNC_AT_DFU_DFUADR) function, with the desired partition, to get the offset, length and value for updating it.

> [!NOTE]
> A status code of [WINC_STATUS_DFU_ADDRESS_WARNING](#AN_STATUS_DFU_ADDRESS_WARNING) is a warning that the other partition does not contain a bootable firmware image. If the user proceeds in spite of this warning and step 4 does not complete for any reason, the device will reach a state in which it contains no bootable firmware images. In that situation, repeating step 4 should recover the device, so long as the user still has the firmware image available.

> [!NOTE]
> Save the value of the NVM partition address for use during step 4.

#### 3. Boot the device in DFU mode

Boot the device in DFU mode using the following steps:

1.  Assert WINCS02 pin NMCLR (low).

2.  Write to WINCS02 pins PB0 (Clock) and PB1 (Data) to send the DFU Test Mode Entry pattern "MCHP".

3.  Deassert WINCS02 pin NMCLR.

#### 4. Erase and program the NVM partition

Configure pins PB0 and PB1 for UART Rx and Tx respectively.

Use Programming Executive (PE) commands to erase the NVM partition, at the address obtained during step 2.

Use Programming Executive (PE) commands to program the new firmware image into the NVM partition, at the address obtained during step 2.

---
### Function Reference:

<a id="AN_FUNC_AT_DFU_DFUADR"></a>
#### WINC_CmdDFUADR

##### Description

This function is used to get the parameters for modifying the little endian address field of a DFU image.

    bool WINC_CmdDFUADR
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t partition
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>partition</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>The partition into which the DFU image will be programmed.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>ALTERNATE</p></td>
<td style="text-align: left;"><p>Alternate partition (recommended).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CURRENT</p></td>
<td style="text-align: left;"><p>Current partition.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>LOW</p></td>
<td style="text-align: left;"><p>Low partition.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>HIGH</p></td>
<td style="text-align: left;"><p>High partition.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<OFFSET\>,\<LENGTH\>,\<VALUE\> | Parameters for modifying the little endian address field of a DFU image |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OFFSET&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Offset (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALUE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Value to write to field in DFU image<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_DFU_DFUSEQ"></a>
#### WINC_CmdDFUSEQ

##### Description

This function is used to get the parameters for modifying the little endian sequence number field of a DFU image.

    bool WINC_CmdDFUSEQ
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t imageState
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>imageState</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>The desired state of the DFU image after programming.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>LATENT</p></td>
<td style="text-align: left;"><p>Latent image (will not run until activated).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ACTIVATED</p></td>
<td style="text-align: left;"><p>Activated image.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<OFFSET\>,\<LENGTH\>,\<VALUE\> | Parameters for modifying the little endian sequence number field of a DFU image |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OFFSET&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Offset (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALUE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Value to write to field in DFU image<br />
</p></td>
</tr>
</tbody>
</table>

---
---
### Examples:

<a id="EXAMPLE_154f5dd58fe255da7480e1634642e778c98de910"></a>
**Example of using [WINC_CmdDFUADR](#AN_FUNC_AT_DFU_DFUADR) and [WINC_CmdDFUSEQ](#AN_FUNC_AT_DFU_DFUSEQ)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Get parameters for making an image for the alternate partition
    APP->>API: WINC_CmdDFUADR(0)
    Note left of API: Offset 20, length 4, value 0x600F0000
    API->>APP: Response:WINC_CMD_ID_DFUADR(20,4,0x600F0000)
    API->>APP: Status:WINC_CMD_ID_DFUADR(OK)
    Note right of APP: Get parameters for making an image for the current partition
    APP->>API: WINC_CmdDFUADR(1)
    Note left of API: Offset 20, length 4, value 0x60000000
    API->>APP: Response:WINC_CMD_ID_DFUADR(20,4,0x60000000)
    API->>APP: Status:WINC_CMD_ID_DFUADR(ERROR:30.0,"No Bootable Image In Other Partition")
    Note right of APP: Get parameters for making an activated image
    APP->>API: WINC_CmdDFUSEQ(0)
    Note left of API: Offset 0, length 4, value 0xFFEEDDC0
    API->>APP: Response:WINC_CMD_ID_DFUSEQ(0,4,0xFFEEDDC0)
    API->>APP: Status:WINC_CMD_ID_DFUSEQ(OK)
    Note right of APP: Get parameters for making a latent image
    APP->>API: WINC_CmdDFUSEQ(1)
    Note left of API: Offset 0, length 4, value 0xFFFFFFFF
    API->>APP: Response:WINC_CMD_ID_DFUSEQ(0,4,0xFFFFFFFF)
    API->>APP: Status:WINC_CMD_ID_DFUSEQ(OK)
```

---
<a id="AN_MOD_PPS"></a>
## PPS (Module ID = 31)

### Introduction

The WINCS02 device supports two advanced power-saving modes designed to reduce current consumption in typical IoT and embedded applications:

- **Platform Power-Save (PPS)** mode places the CPU and hardware peripherals into sleep modes - most clocks and peripherals are powered down, leaving only essential hardware blocks active. This drastically reduces power consumption while preserving Wi-Fi connectivity and system context, enabling rapid wake-up and seamless operation.

- **EXtreme Deep Sleep (XDS)** enters the device’s lowest power state, with all peripherals powered down and system context lost. This mode achieves maximum power savings for long standby periods where Wi-Fi or network connections are not required. Waking from XDS triggers a full system reboot.

#### PPS Operation Details

When **PPS** is enabled, the system automatically transitions into PPS mode during idle periods, minimising power while maintaining system and Wi-Fi state. This includes active protocol connections, Wi-Fi association, and buffered data queues.

##### Wake-Up Triggers

There are a number of events that will cause the WINCS02 to wake when PPS is active:

- Internal timers or internal scheduled events

  - These will be accounted for when PPS calculates its sleep duration for the next period, ensuring it wakes up in time to process the next event/timer

- Host MCU activity over the SPI interface

  - Attempts to use the SPI interface will wake the WINCS02 immediately

- In the absence of internal timers or external triggers, PPS will wake the WINCS02 after 10 seconds

Once awake, the WINCS02 will run until the next idle period, whereby it will transition into PPS mode again.

##### Wi-Fi Power Save Mode during PPS

When PPS is enabled and Wi-Fi is connected, the WINCS02 operates Wi-Fi Legacy Powersave to minimise power consumption while maintaining network connectivity.

###### Listen Interval

The WINCS02 wakes periodically based on the configured Wi-Fi Listen Interval, which determines how often it wakes to listen for buffered traffic from the AP. By default, this interval is 10 beacon periods, roughly equivalent to 1 second (typical beacon interval is 102.4 ms).

###### DTIM (Delivery Traffic Indication Message) Awareness

To efficiently receive broadcast and multicast traffic buffered by the AP, the device aims to wake on the closest DTIM period aligned with the configured listen interval. The DTIM is a special beacon that signals buffered broadcast/multicast data transmission by the AP. For example, if the Listen Interval is set to 10 beacon periods (default) and the AP’s DTIM period is 3, the WINCS02 will wake after 9 beacon periods (i.e. on the 3rd DTIM) instead of exactly after 10 beacons. This alignment maximises power savings by minimising unnecessary wake events while ensuring timely reception of important broadcast traffic.

##### Sleep Timing Accuracy

To optimise power saving and accuracy of wake intervals, it is strongly recommended to connect and enable a secondary oscillator (SOSC) clocked at 32768 Khz. The SOSC provides a high-accuracy timing source during sleep, allowing for more precise wake-up timing when using longer sleep durations.

##### PPS Pause

PPS Pause allows temporarily suspending Platform Power-Save operation without fully disabling it. This is useful during periods where continuous device responsiveness is required, such as during critical command sequences, firmware updates or other high-activity times when entering sleep state would be undesirable.

###### How PPS Pause Works

- When a pause is active, the system remains fully awake, bypassing PPS sleep transitions.

- Multiple pause commands can be issued sequentially, and the pause durations extend the total pause period.

- After all active pause timers expire, the WINCS02 automatically sends an Automatic Event Callback (AEC) for informational purposes, to indicate that PPS will now resume.

- Once the pause period has expired, the system will return to normal PPS operation, entering low-power sleep during idle periods.

##### Wake-Up via SPI

- The SPI core supports **clockless operation**, so no additional hardware signals or protocol changes are needed to wake the device.

- The host MCU simply starts a SPI transaction to wake the WINCS02.

> [!NOTE]
> - Wake-up latency from PPS mode is approximately **4 ms**.

##### Command Transmission and AUTOSLEEP

- The WINCS02 remains awake while processing the SPI transactions and any corresponding Wi-Fi or protocol activity.

- Once no further commands or traffic are outstanding, the system returns to PPS sleep.

- The AUTOSLEEP parameter controls how long the WINCS02 remains awake, allowing multiple transactions to be sent without re-waking each time:

  - Configured with `WINC_CmdPPSC(handle,WINC_CFG_PARAM_ID_PPS_AUTO_SLEEP_TIMEOUT,WINC_TYPE_INTEGER,<ms>,0)`

  - Extends the time WINCS02 stays awake after waking for a SPI transaction, providing the host extra time to send multiple SPI transactions.

---
##### Configuration and Usage

See example [Configuring and enabling PPS](#EXAMPLE_PPS_1)

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Configure Listen Interval to 30 beacon periods (around 3 seconds)
    APP->>API: WINC_CmdWIFIC(21,30)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Enable Secondary Oscillator (optional)
    APP->>API: WINC_CmdPPSC(1,1)
    API->>APP: Status:WINC_CMD_ID_PPSC(OK)
    Note right of APP: Set AUTOSLEEP Timeout to 100ms
    APP->>API: WINC_CmdPPSC(2,100)
    API->>APP: Status:WINC_CMD_ID_PPSC(OK)
    Note right of APP: Set PPS to be enabled for 60 seconds
    APP->>API: WINC_CmdPPSC(3,60)
    API->>APP: Status:WINC_CMD_ID_PPSC(OK)
    Note right of APP: Enable PPS Mode
    APP->>API: WINC_CmdPPS(1)
    API->>APP: Status:WINC_CMD_ID_PPS(OK)
    Note right of APP: Pause PPS temporarily for 5 seconds (timeout extends if sent repeatedly)
    APP->>API: WINC_CmdPPS(2)
    API->>APP: Status:WINC_CMD_ID_PPS(OK)
    Note right of APP: Terminate PPS Operation
    APP->>API: WINC_CmdPPS(0)
    API->>APP: Status:WINC_CMD_ID_PPS(OK)
```

---
#### EXtreme Deep Sleep (XDS)

XDS mode puts the WINCS02 into the absolute lowest power state, with all but the bare minimum clocks and peripherals powered off. Use this mode when long idle periods are expected and Wi-Fi connectivity/state retention is not required.

##### XDS characteristics

- The system loses all context and network state (no Wi-Fi connection or open sockets preserved).

- The only wake-up methods available are hardware signals:

  - Pull **MCLR** pin low (hardware reset)

> [!NOTE]
> Wake-up triggers a **full system reboot**.

##### XDS Operation details

To enter XDS mode, use the following API:

`WINC_CmdPPS(handle, WDRV_WINC_POWERSAVE_XDS_MODE)`

#### Summary

##### PPS (Platform Power Save)

Balances power saving with connectivity. Maintains Wi-Fi and protocol state. Supports low-latency wake-up. Recommended to enable SOSC for precise timing.

##### XDS (EXtreme Deep Sleep)

Maximises power saving by powering down all but the bare minimum device functions. Requires hardware wake-up and full reboot on wake. Used for extended idle periods with no connectivity requirements.

---
### Function Reference:

#### WINC_CmdPPSC

##### Description

This function is used to read or set the PPS configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdPPSC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDPPSC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_PPS_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SEC_OSC_ENABLED</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>Use secondary oscillator<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>OFF</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ON</p></td>
<td style="text-align: left;"><p>On.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>AUTO_SLEEP_TIMEOUT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Timeout between commands before entering sleep measured in ms<br />
<br />
Valid range is 10 to 3000<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DURATION</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Time to maintain PPS mode in seconds (0 for infinite)<br />
<br />
Valid range is 0 to 86400<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdPPS

##### Description

This function allows the firmware to change the state of platform power save.

    bool WINC_CmdPPS
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t ppsState
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>ppsState</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>PPS State.<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLE</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PPS</p></td>
<td style="text-align: left;"><p>PPS mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>XDS</p></td>
<td style="text-align: left;"><p>XDS mode.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### WINC_CmdPPSPAUSE

##### Description

This function allows the firmware to change the state of platform power save.

    bool WINC_CmdPPSPAUSE
    (
        WINC_CMD_REQ_HANDLE handle
        uint16_t pauseTime
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pauseTime</p></td>
<td style="text-align: left;"><p>uint16_t</p></td>
<td style="text-align: left;"><p>PPS pause time in sec.<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_PPS

##### Description

**Indication of PPS event.**

| AEC           | Description |
|---------------|-------------|
| \<PPS EVENT\> | PPS Event   |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PPS EVENT&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Event code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>TIMEOUT</p></td>
<td style="text-align: left;"><p>Timeout.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PAUSE_EXPIRED</p></td>
<td style="text-align: left;"><p>Pause expired.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_PPS_1"></a>
**Configuring and enabling PPS**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Configure Listen Interval to 30 beacon periods (around 3 seconds)
    APP->>API: WINC_CmdWIFIC(21,30)
    API->>APP: Status:WINC_CMD_ID_WIFIC(OK)
    Note right of APP: Enable Secondary Oscillator (optional)
    APP->>API: WINC_CmdPPSC(1,1)
    API->>APP: Status:WINC_CMD_ID_PPSC(OK)
    Note right of APP: Set AUTOSLEEP Timeout to 100ms
    APP->>API: WINC_CmdPPSC(2,100)
    API->>APP: Status:WINC_CMD_ID_PPSC(OK)
    Note right of APP: Set PPS to be enabled for 60 seconds
    APP->>API: WINC_CmdPPSC(3,60)
    API->>APP: Status:WINC_CMD_ID_PPSC(OK)
    Note right of APP: Enable PPS Mode
    APP->>API: WINC_CmdPPS(1)
    API->>APP: Status:WINC_CMD_ID_PPS(OK)
    Note right of APP: Pause PPS temporarily for 5 seconds (timeout extends if sent repeatedly)
    APP->>API: WINC_CmdPPS(2)
    API->>APP: Status:WINC_CMD_ID_PPS(OK)
    Note right of APP: Terminate PPS Operation
    APP->>API: WINC_CmdPPS(0)
    API->>APP: Status:WINC_CMD_ID_PPS(OK)
```

---
## SYSLOG (Module ID = 32)

### Function Reference:

<a id="AN_FUNC_AT_SYSLOG_SYSLOGC"></a>
#### WINC_CmdSYSLOGC

##### Description

This function is used to read or set the SYSLOG configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdSYSLOGC
    (
        WINC_CMD_REQ_HANDLE handle
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDSYSLOGC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_SYSLOG_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>BOOL<br />
</p></td>
<td style="text-align: left;"><p>DCE’s SYSLOG<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DISABLED</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ENABLED</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### WINC_AEC_ID_SYSLOG

##### Description

**SYSLOG Event.**

| AEC                                                        | Description |
|------------------------------------------------------------|-------------|
| \<TIMESTAMP\>,\<MODULE_ID\>,\<EVENT_SEVERITY\>,\<MESSAGE\> | Log message |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TIMESTAMP&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Log timestamp<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MODULE_ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
STRING<br />
BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Module ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;EVENT_SEVERITY&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Event severity<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>EMERGENCY</p></td>
<td style="text-align: left;"><p>Emergency.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ALERT</p></td>
<td style="text-align: left;"><p>Alert.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>CRITICAL</p></td>
<td style="text-align: left;"><p>Critical.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>ERROR</p></td>
<td style="text-align: left;"><p>Error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WARNING</p></td>
<td style="text-align: left;"><p>Warning.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>NOTICE</p></td>
<td style="text-align: left;"><p>Notice.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>INFO</p></td>
<td style="text-align: left;"><p>Info.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>DEBUG</p></td>
<td style="text-align: left;"><p>Debug.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MESSAGE&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Log message<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_ARB"></a>
## ARB (Module ID = 33)

### Introduction

The WINCS02 device has an anti-rollback counter (ARB) which can be used to prevent vulnerable firmware from running on the device.

The value in the ARB is between 0 and 127 and can be increased but never decreased. If a firmware image has a security level which is lower than the value in the ARB, then that image will not boot.

Use the [WINC_CmdARB](#AN_FUNC_AT_ARB_ARB) function to get the current value in the device’s ARB and the current firmware’s security level. If the device’s ARB is lower than the firmware’s security level, then consider increasing the value in the device’s ARB to improve the security of the device.

For information about the security benefits of increasing the device’s ARB, refer to WINCS02 device firmware release notes at microchip.com.

To increase the value in the device’s ARB, use the [WINC_CmdARB](#AN_FUNC_AT_ARB_ARB) function.

> [!CAUTION]
> If the device has an image present in the alternate NVM partition, be aware that increasing the device’s ARB may invalidate that image.

---
### Function Reference:

<a id="AN_FUNC_AT_ARB_ARB"></a>
#### WINC_CmdARB

##### Description

This function is used to get or increase the WINC’s ARB value, and to get the current firmware’s security level.

    bool WINC_CmdARB
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t optValue
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optValue</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>The value to which to increase the DCE’s ARB.<br />
</p>
<p>optValue will be ignored if its value is<br />
WINC_CMDARB_VALUE_IGNORE_VAL.</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| \<VALUE\>,\<FW_SECURITY\> | The DCE’s ARB value and the current firmware’s security level |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;VALUE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>DCE’s ARB value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FW_SECURITY&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Current firmware’s security level<br />
</p></td>
</tr>
</tbody>
</table>

---
---
### Examples:

<a id="EXAMPLE_43ad9746b269d7ef860794a7d75c34ef47c94f97"></a>
**Example of using [WINC_CmdARB](#AN_FUNC_AT_ARB_ARB)**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Get the DCE's ARB value and the current firmware's security level
    APP->>API: WINC_CmdARB()
    Note left of API: DCE's ARB value is 0; current firmware's security level is 1
    API->>APP: Response:WINC_CMD_ID_ARB(0,1)
    API->>APP: Status:WINC_CMD_ID_ARB(OK)
    Note right of APP: Increase the DCE's ARB value to 1
    APP->>API: WINC_CmdARB(1)
    Note left of API: DCE's ARB value is 1; current firmware's security level is 1
    API->>APP: Response:WINC_CMD_ID_ARB(1,1)
    API->>APP: Status:WINC_CMD_ID_ARB(OK)
    Note right of APP: Increase the DCE's ARB value to 1
    APP->>API: WINC_CmdARB(1)
    Note left of API: DCE's ARB value is 1; current firmware's security level is 1
    API->>APP: Response:WINC_CMD_ID_ARB(1,1)
    API->>APP: Status:WINC_CMD_ID_ARB(ERROR:33.0,"The Value Provided Would Not Increase The ARB")
    Note right of APP: Increase the DCE's ARB value to 2
    APP->>API: WINC_CmdARB(2)
    Note left of API: DCE's ARB value is 1; current firmware's security level is 1
    API->>APP: Response:WINC_CMD_ID_ARB(1,1)
    API->>APP: Status:WINC_CMD_ID_ARB(ERROR:33.1,"The Value Provided Would Invalidate The Current Image")
```

---
<a id="AN_MOD_HTTP"></a>
## HTTP (Module ID = 34)

### Introduction

The WINCS02 supports comprehensive HTTP client capabilities via its API, enabling easy integration with web servers for a variety of applications such as firmware updates, data retrieval, and cloud communication.

#### Key Features

##### HTTP Configuration Management

Configure HTTP connection parameters including the server address (hostname or IP), port number, request path, TLS settings, timeouts, and more. These settings ensure flexible connection setups to suit diverse network environments and security needs.

##### HTTP GET Requests

Perform HTTP GET operations to request resources from a web server. You can specify the resource path, enabling the retrieval of files, JSON data, or other web content.

##### Direct File Downloads to Flash Filesystem

Download HTTP response data directly into the device’s flash filesystem. By configuring a local filename and file type, the downloaded content is automatically stored in the flash filesystem without requiring manual data reading. This is particularly useful for downloading certificates, configuration files, firmware images, or other persistent data. The filesystem supports multiple file types including USER files, certificates (CERT), private keys (PRIKEY), Diffie-Hellman parameters (DHPARAM), and configuration files (CFG).

##### Data Reading

Efficiently read HTTP response data in chunks of defined length. This allows controlled data transfer suitable for devices with limited memory. Manual data reading can be performed using [WINC_CmdHTTPRD](#AN_FUNC_AT_HTTP_HTTPRD) when not downloading directly to the filesystem.

##### Response Handling

Receive detailed response information such as HTTP status codes, response headers, and body content, including full notification when the response body is completely received.

##### Data Integrity Verification

Optional hash calculation (SHA, SHA256, SHA224, SHA512, SHA384) during download to verify data integrity. The hash is computed automatically and reported in the [WINC_AEC_ID_HTTPBODYEND](#AN_AEC_AT_HTTP_HTTPBODYEND) asynchronous event.

##### Security Support

Integrated TLS configuration allows HTTPS connections ensuring data privacy and integrity.

#### How It Works

##### Manual Data Retrieval

See examples [HTTPS download](#EXAMPLE_HTTP_1) and [HTTPS download from TCP socket](#EXAMPLE_HTTP_2).

- Configure the HTTP client using [WINC_CmdHTTPC](#AN_FUNC_AT_HTTP_HTTPC) to set the hostname, port, path, and other parameters.

- Optionally configure TLS with [WINC_CmdTLSC](#AN_FUNC_AT_TLS_TLSC) for encrypted HTTPS connections.

- Initiate an HTTP GET request via [WINC_CmdHTTPGET](#AN_FUNC_AT_HTTP_HTTPGET).

- Monitor response status and headers through AECs ([WINC_AEC_ID_HTTPRSPCODE](#AN_AEC_AT_HTTP_HTTPRSPCODE), [WINC_AEC_ID_HTTPRSPFIELD](#AN_AEC_AT_HTTP_HTTPRSPFIELD)).

- Read the HTTP response body in manageable blocks using [WINC_CmdHTTPRD](#AN_FUNC_AT_HTTP_HTTPRD).

- Close the connection cleanly with [WINC_CmdHTTPCL](#AN_FUNC_AT_HTTP_HTTPCL) after data transfer completes.

##### Direct Filesystem Download

See example [File download to local filesystem](#EXAMPLE_HTTP_3).

- Configure the HTTP client using [WINC_CmdHTTPC](#AN_FUNC_AT_HTTP_HTTPC) to set the hostname, port, path, and other parameters.

- Set the local filename using [WINC_CmdHTTPC](#AN_FUNC_AT_HTTP_HTTPC) ID 20 (FILENAME parameter).

- Set the local file type using [WINC_CmdHTTPC](#AN_FUNC_AT_HTTP_HTTPC) ID 21 (FILETYPE parameter):

  - 0 = USER (user files)

  - 1 = CERT (certificates)

  - 2 = PRIKEY (private keys)

  - 3 = DHPARAM (Diffie-Hellman parameters)

  - 20 = CFG (configuration files)

- Optionally configure hash verification using [WINC_CmdHTTPC](#AN_FUNC_AT_HTTP_HTTPC) ID 22 (CHECK_MODE parameter):

  - 0 = NONE (no hash verification)

  - 10 = SHA

  - 11 = SHA256

  - 12 = SHA224

  - 13 = SHA512

  - 14 = SHA384

- Optionally configure TLS with [WINC_CmdTLSC](#AN_FUNC_AT_TLS_TLSC) for encrypted HTTPS connections.

- Initiate an HTTP GET request via [WINC_CmdHTTPGET](#AN_FUNC_AT_HTTP_HTTPGET).

- Monitor response status and headers through AECs ([WINC_AEC_ID_HTTPRSPCODE](#AN_AEC_AT_HTTP_HTTPRSPCODE), [WINC_AEC_ID_HTTPRSPFIELD](#AN_AEC_AT_HTTP_HTTPRSPFIELD)).

- The downloaded data is automatically written to the flash filesystem.

- When complete, [WINC_AEC_ID_HTTPBODYEND](#AN_AEC_AT_HTTP_HTTPBODYEND) is sent with total bytes downloaded and optional hash value.

- A filesystem update notification [WINC_AEC_ID_FSUP](#AN_AEC_AT_FS_FLFS_FSUP) confirms the file has been stored.

- The connection closes automatically (non-persistent connection mode).

> [!NOTE]
> When a local filename is configured, the HTTP client operates in non-persistent connection mode and automatically writes received data to the filesystem. Manual data reading via [WINC_CmdHTTPRD](#AN_FUNC_AT_HTTP_HTTPRD) is not available in this mode.

#### Advanced Features

##### Using an Existing Socket Connection

The HTTP client can utilize an existing TCP socket connection instead of creating its own. This is useful when you need more control over the connection setup, such as pre-configuring socket options or managing connection pooling.

> [!NOTE]
> When using an existing socket, do not configure the HOST (ID 2) or PORT (ID 3) parameters in the HTTP configuration.

##### Path Override with Query Parameters

When issuing an HTTP GET request, you can specify a complete path including query parameters and fragments as the second parameter to [WINC_CmdHTTPGET](#AN_FUNC_AT_HTTP_HTTPGET). This overrides the PATH (ID 4) and FILE (ID 5) configuration parameters for that specific request. See example [HTTPGET with path and query/fragments](#EXAMPLE_HTTP_4).

##### HTTP Authentication

HTTP basic authentication can be implemented by providing additional request headers using [WINC_CmdHTTPC](#AN_FUNC_AT_HTTP_HTTPC) ID 8 (REQ_HEADERS parameter). The authorization header should contain the Base64-encoded credentials.

See example [HTTP basic authentication using additional request headers](#EXAMPLE_HTTP_5).

##### Reading Configuration Values

The read-only configuration parameter **CONTENT_LENGTH** reports the Content-Length value from the HTTP response headers after they are received.

---
### Function Reference:

<a id="AN_FUNC_AT_HTTP_HTTPC"></a>
#### WINC_CmdHTTPC

##### Description

This function is used to read or set the HTTP configuration.

This function is a configuration function which supports setting and getting parameter values. The behaviour of configuration functions is described in general in the [Configuration Functions](#_configuration_functions) section.

    bool WINC_CmdHTTPC
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t optConf
        int32_t optId
        WINC_TYPE typeOptVal
        uintptr_t optVal
        size_t lenOptVal
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optConf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Configuration number.<br />
</p>
<p>optConf will be ignored if its value is<br />
WINC_CMDHTTPC_CONF_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optId</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Parameter ID number.<br />
</p>
<p>optId will be ignored if its value is<br />
WINC_CMDHTTPC_ID_IGNORE_VAL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>typeOptVal</p></td>
<td style="text-align: left;"><p>WINC_TYPE</p></td>
<td style="text-align: left;"><p>Type of optVal.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>optVal</p></td>
<td style="text-align: left;"><p>uintptr_t</p></td>
<td style="text-align: left;"><p>Parameter value.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptVal</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of optVal.<br />
</p></td>
</tr>
</tbody>
</table>

| Response          | Description   |
|-------------------|---------------|
| \<CONF\>,\<CONF\> | List response |
| \<ID\>,\<VAL\>    | Read response |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Any</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters (WINC_CFG_PARAM_ID_HTTP_*)</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 17%" />
<col style="width: 49%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>PRESET</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DEFAULT</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>HOST</p></td>
<td style="text-align: left;"><p>STRING<br />
IPV4ADDR<br />
IPV6ADDR<br />
</p></td>
<td style="text-align: left;"><p>Host domain name or IP address<br />
Maximum length of string is 255<br />
Format of IPv4 address is<br />
A1|A2|A3|A4 = A1.A2.A3.A4<br />
Format of IPv6 address is<br />
A1|…​|A16 = A1A2::A15A16<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>PORT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Listening port<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>PATH</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Path to remote file<br />
Maximum length of string is 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>FILE</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Remote filename<br />
Maximum length of string is 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>TIMEOUT</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Timeout in seconds<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>TLS_CONF</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>REQ_HEADERS</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Additional request headers<br />
Maximum length of string is 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SOCKET_ID</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Socket ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>FILENAME</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>Local filename<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>FILETYPE</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Local file type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>USER</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>CERT</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PRIKEY</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DHPARAM</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>CFG</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>CHECK_MODE</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Checking mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>NONE</p></td>
<td style="text-align: left;"><p>None.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>CONTENT_LENGTH</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Content length<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>100</p></td>
<td style="text-align: left;"><p>ASYNC_NEXT_OFFSET</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Async next data offset<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>101</p></td>
<td style="text-align: left;"><p>ASYNC_WIN_SZ</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Async window size<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>102</p></td>
<td style="text-align: left;"><p>ASYNC_MAX_FRM_SZ</p></td>
<td style="text-align: left;"><p>INTEGER_UNSIGNED<br />
</p></td>
<td style="text-align: left;"><p>Async maximum frame size<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_HTTP_HTTPGET"></a>
#### WINC_CmdHTTPGET

##### Description

This function performs an HTTP GET operation.

    bool WINC_CmdHTTPGET
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t conf
        const uint8_t* pOptPath
        size_t lenOptPath
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>conf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Configuration number.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>pOptPath</p></td>
<td style="text-align: left;"><p>const uint8_t*</p></td>
<td style="text-align: left;"><p>Resource path.<br />
</p>
<p>pOptPath will be ignored if its value is NULL.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>lenOptPath</p></td>
<td style="text-align: left;"><p>size_t</p></td>
<td style="text-align: left;"><p>Length of pOptPath.<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_HTTP_HTTPRD"></a>
#### WINC_CmdHTTPRD

##### Description

This function performs an HTTP data read operation.

    bool WINC_CmdHTTPRD
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t conf
        int32_t length
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>conf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Configuration number.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>length</p></td>
<td style="text-align: left;"><p>int32_t</p></td>
<td style="text-align: left;"><p>Number of bytes.<br />
</p></td>
</tr>
</tbody>
</table>

| Response                                       | Description         |
|------------------------------------------------|---------------------|
| \<CONF\>,\<DATA_LEN\>,\<DATA_OFFSET\>,\<DATA\> | HTTP body data read |

**Response Format**

<table>
<caption>Response Element Description</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LEN&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_OFFSET&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Offset of data bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>HTTP data<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_FUNC_AT_HTTP_HTTPCL"></a>
#### WINC_CmdHTTPCL

##### Description

This function performs an HTTP close operation.

    bool WINC_CmdHTTPCL
    (
        WINC_CMD_REQ_HANDLE handle
        uint8_t conf
    )

<table>
<caption>Function Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>handle</p></td>
<td style="text-align: left;"><p>WINC_CMD_REQ_HANDLE</p></td>
<td style="text-align: left;"><p>Command request session handle.<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>conf</p></td>
<td style="text-align: left;"><p>uint8_t</p></td>
<td style="text-align: left;"><p>Configuration number.<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_HTTP_HTTPRSPCODE"></a>
#### WINC_AEC_ID_HTTPRSPCODE

##### Description

**HTTP response code.**

| AEC                                    | Description        |
|----------------------------------------|--------------------|
| \<CONF\>,\<RSP_PROTOCOL\>,\<RSP_CODE\> | HTTP response code |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP response protocol version<br />
<br />
Value is 1.1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP response code<br />
<br />
Valid range is 100 to 599<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_HTTP_HTTPRSPFIELD"></a>
#### WINC_AEC_ID_HTTPRSPFIELD

##### Description

**HTTP response field.**

| AEC                                             | Description         |
|-------------------------------------------------|---------------------|
| \<CONF\>,\<RSP_FIELD_NAME\>,\<RSP_FIELD_VALUE\> | HTTP response field |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_FIELD_NAME&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>HTTP response field name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_FIELD_VALUE&gt;</p></td>
<td style="text-align: left;"><p>STRING<br />
</p></td>
<td style="text-align: left;"><p>HTTP response field value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_HTTPBODYRX

##### Description

**HTTP body.**

| AEC                                            | Description             |
|------------------------------------------------|-------------------------|
| \<CONF\>,\<PEND_DATA\>                         | HTTP body data notify   |
| \<CONF\>,\<DATA_LEN\>,\<DATA_OFFSET\>,\<DATA\> | HTTP body data received |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LEN&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_OFFSET&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Offset of data bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>HTTP data<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_HTTP_HTTPBODYEND"></a>
#### WINC_AEC_ID_HTTPBODYEND

##### Description

**HTTP body end.**

| AEC                                          | Description        |
|----------------------------------------------|--------------------|
| \<CONF\>,\<DATA_LEN\>                        | HTTP body data end |
| \<CONF\>,\<DATA_LEN\>,\<HASH_TYPE\>,\<HASH\> | HTTP body data end |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LEN&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;HASH_TYPE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Hash algorithm<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 28%" />
<col style="width: 57%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Value</th>
<th style="text-align: left;">Label</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;HASH&gt;</p></td>
<td style="text-align: left;"><p>BYTE_ARRAY<br />
</p></td>
<td style="text-align: left;"><p>Hash<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_HTTPCL

##### Description

**HTTP close.**

| AEC      | Description |
|----------|-------------|
| \<CONF\> | HTTP close  |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
</tbody>
</table>

---
#### WINC_AEC_ID_HTTPERR

##### Description

**HTTP error.**

| AEC                     | Description |
|-------------------------|-------------|
| \<CONF\>,\<ERROR_CODE\> | HTTP error  |

**AEC Syntax**

<table>
<caption>AEC Element Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Element Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>INTEGER<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

<a id="EXAMPLE_HTTP_1"></a>
**HTTPS download**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note left of API: Wait for time for correct TLS operation
    API->>APP: AEC:WINC_AEC_ID_TIME(3969426905)
    Note right of APP: Set the server CA certificate
    APP->>API: WINC_CmdTLSC(1,1,"ServerCACert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set the server domain
    APP->>API: WINC_CmdTLSC(1,6,"example.com")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set the server hostname
    APP->>API: WINC_CmdHTTPC(1,2,"www.example.com")
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Set the HTTPS port number
    APP->>API: WINC_CmdHTTPC(1,3,443)
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Set the file path
    APP->>API: WINC_CmdHTTPC(1,5,"/examplefile.bin")
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Set 10 second timeout
    APP->>API: WINC_CmdHTTPC(1,6,10)
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Use TLSC index 1
    APP->>API: WINC_CmdHTTPC(1,7,1)
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Get resource configuration 1
    APP->>API: WINC_CmdHTTPGET(1)
    API->>APP: Status:WINC_CMD_ID_HTTPGET(OK)
    Note left of API: Server responds 200 OK
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPCODE(1,1.1,200)
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Date","Wed, 5 Nov 2025 11:23:45 GMT")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Last-Modified","Sun, 12 Oct 2025 21:15:27 GMT")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Accept-Ranges","bytes")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Content-Type","binary/octet-stream")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Content-Length","2563")
    Note left of API: 1460 bytes received
    API->>APP: AEC:WINC_AEC_ID_HTTPBODYRX(1,1460)
    Note right of APP: Read 1460 bytes
    APP->>API: WINC_CmdHTTPRD(1,1460)
    API->>APP: Response:WINC_CMD_ID_HTTPRD(1,1460,0,[FFFFFFFF...74780000])
    API->>APP: Status:WINC_CMD_ID_HTTPRD(OK)
    Note left of API: 1103 bytes received
    API->>APP: AEC:WINC_AEC_ID_HTTPBODYRX(1,1103)
    Note left of API: All body data received
    API->>APP: AEC:WINC_AEC_ID_HTTPBODYEND(1,2563)
    Note right of APP: Read 1103 bytes
    APP->>API: WINC_CmdHTTPRD(1,1103)
    API->>APP: Response:WINC_CMD_ID_HTTPRD(1,1103,1460,[65205072...1102D0A1])
    API->>APP: Status:WINC_CMD_ID_HTTPRD(OK)
    Note left of API: Remote server closed connection
    API->>APP: AEC:WINC_AEC_ID_HTTPCL(1)
```

<a id="EXAMPLE_HTTP_2"></a>
**HTTPS download from TCP socket**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note left of API: Wait for time for correct TLS operation
    API->>APP: AEC:WINC_AEC_ID_TIME(3969426905)
    Note right of APP: Open TCP socket
    APP->>API: WINC_CmdSOCKO(2)
    API->>APP: Response:WINC_CMD_ID_SOCKO(18870)
    API->>APP: Status:WINC_CMD_ID_SOCKO(OK)
    Note right of APP: Set the server CA certificate
    APP->>API: WINC_CmdTLSC(1,1,"ServerCACert")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set the server domain
    APP->>API: WINC_CmdTLSC(1,6,"example.com")
    API->>APP: Status:WINC_CMD_ID_TLSC(OK)
    Note right of APP: Set the file path
    APP->>API: WINC_CmdHTTPC(1,5,"/examplefile.bin")
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Set 10 second timeout
    APP->>API: WINC_CmdHTTPC(1,6,10)
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Assign socket ID to HTTP configuration
    APP->>API: WINC_CmdHTTPC(1,10,18870)
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Upgrade socket to TLS
    APP->>API: WINC_CmdSOCKTLS(18870,1)
    API->>APP: Status:WINC_CMD_ID_SOCKTLS(OK)
    Note right of APP: Bind socket to server
    APP->>API: WINC_CmdSOCKBR(18870,"www.example.com",443)
    API->>APP: Status:WINC_CMD_ID_SOCKBR(OK)
    Note left of API: Socket connected
    API->>APP: AEC:WINC_AEC_ID_SOCKIND(18870,"1.2.3.4",61955,"5.6.7.8",443)
    Note left of API: Socket upgraded to TLS
    API->>APP: AEC:WINC_AEC_ID_SOCKTLS(18870)
    Note right of APP: Get resource configuration 1
    APP->>API: WINC_CmdHTTPGET(1)
    API->>APP: Status:WINC_CMD_ID_HTTPGET(OK)
    Note left of API: Server responds 200 OK
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPCODE(1,1.1,200)
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Date","Wed, 5 Nov 2025 11:23:45 GMT")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Last-Modified","Sun, 12 Oct 2025 21:15:27 GMT")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Accept-Ranges","bytes")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Content-Type","binary/octet-stream")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Content-Length","2563")
    Note left of API: 1460 bytes received
    API->>APP: AEC:WINC_AEC_ID_HTTPBODYRX(1,1460)
    Note right of APP: Read 1460 bytes
    APP->>API: WINC_CmdHTTPRD(1,1460)
    API->>APP: Response:WINC_CMD_ID_HTTPRD(1,1460,0,[FFFFFFFF...74780000])
    API->>APP: Status:WINC_CMD_ID_HTTPRD(OK)
    Note left of API: 1103 bytes received
    API->>APP: AEC:WINC_AEC_ID_HTTPBODYRX(1,1103)
    Note left of API: All body data received
    API->>APP: AEC:WINC_AEC_ID_HTTPBODYEND(1,2563)
    Note right of APP: Read 1103 bytes
    APP->>API: WINC_CmdHTTPRD(1,1103)
    API->>APP: Response:WINC_CMD_ID_HTTPRD(1,1103,1460,[65205072...1102D0A1])
    API->>APP: Status:WINC_CMD_ID_HTTPRD(OK)
    Note left of API: Remote server closed connection
    API->>APP: AEC:WINC_AEC_ID_HTTPCL(1)
```

<a id="EXAMPLE_HTTP_3"></a>
**File download to local filesystem**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: Set local filename
    APP->>API: WINC_CmdHTTPC(1,20,"testname")
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Set local file type to USER
    APP->>API: WINC_CmdHTTPC(1,21,0)
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
    Note right of APP: Get resource configuration 1
    APP->>API: WINC_CmdHTTPGET(1)
    API->>APP: Status:WINC_CMD_ID_HTTPGET(OK)
    Note left of API: Server responds 200 OK
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPCODE(1,1.1,200)
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Date","Wed, 5 Nov 2025 11:23:45 GMT")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Last-Modified","Sun, 12 Oct 2025 21:15:27 GMT")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Accept-Ranges","bytes")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Content-Type","binary/octet-stream")
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPFIELD(1,"Content-Length","1024")
    Note left of API: All body data received
    API->>APP: AEC:WINC_AEC_ID_HTTPBODYEND(1,1024)
    Note left of API: Filesystem updated
    API->>APP: AEC:WINC_AEC_ID_FSUP(1,0,"testname",1024)
    Note left of API: Remote server closed connection
    API->>APP: AEC:WINC_AEC_ID_HTTPCL(1)
    Note right of APP: Query for USER files
    APP->>API: WINC_CmdFS(2,0)
    Note left of API: File now present in filesystem
    API->>APP: Response:WINC_CMD_ID_FS(2,0,"testname")
    API->>APP: Status:WINC_CMD_ID_FS(OK)
```

<a id="EXAMPLE_HTTP_4"></a>
**HTTPGET with path and query/fragments**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    Note right of APP: afragment"
    APP->>API: WINC_CmdHTTPGET(1,"/anypath/anyfile?att1=val1&att2=val2)
    API->>APP: Status:WINC_CMD_ID_HTTPGET(OK)
    API->>APP: AEC:WINC_AEC_ID_HTTPRSPCODE(1,1.1,200)
```

<a id="EXAMPLE_HTTP_5"></a>
**HTTP basic authentication using additional request headers**

```mermaid
sequenceDiagram
    participant APP as App
    participant API as API
    APP->>API: WINC_CmdHTTPC(1,8,"Authorization: Basic dXNlcm5hbWU6cGFzc3dk")
    API->>APP: Status:WINC_CMD_ID_HTTPC(OK)
```

---
## Berkeley Sockets APIs

### Introduction

This interface provides a Berkeley style sockets API. While closely matching the Berkeley standard API this interface does differ due to the architecture of the WINCS02. Only asynchronous sockets are supported; no function will block.

This API supports:

- IPv4 and IPv6 sockets.

- Datagram (UDP) and streaming (TCP) sockets.

- TLS for TCP sockets.

- Server and client operations.

#### Socket Initialisation

The sockets interface must be initialised before any other socket functions or resources can be used. The function [WINC_SockInit](#AN_FUNC_API_WINC_SOCKINIT) is used to initialise the interface. During initialisation the function will allocate a main slab memory block and ensure all state is reset.

#### Slab Memory Allocation

To avoid causing heap fragmentation the sockets interface uses a preallocated slab architecture to reduce the number of `malloc` and `free` operation. There are two options for how this slab is allocate and managed.

##### Slab Alignment

To assist with architectures where memory alignment is important, the define `WINC_SOCK_SLAB_MEM_ALIGNMENT` can be set to specify the alignment granularity. The starting address of a slab will be aligned to this define, and the size of allocations will be rounded up to the nearest aligned size.

##### Slab Allocation Mode 1

When `WINC_SOCK_SLAB_ALLOC_MODE` is defined to be 1 the sockets interface will use a single slab allocation, created when [WINC_SockInit](#AN_FUNC_API_WINC_SOCKINIT) is called and destroyed when [WINC_SockDeinit](#AN_FUNC_API_WINC_SOCKDEINIT) is called.

The memory requirement for this slab is defined in the [WINC_SOCKET_INIT_TYPE](#AN_FUNC_API_WINC_SOCKET_INIT_TYPE) structure passed to [WINC_SockInit](#AN_FUNC_API_WINC_SOCKINIT). This works out to approximately:

    (WINC_SOCKET_INIT_TYPE.slabSize * WINC_SOCKET_INIT_TYPE.numSlabs) + Overhead

All socket allocations will made from this single slab, therefore the size and number of slabs should be chosen to support the expected memory use of the system for all active sockets.

##### Slab Allocation Mode 2

When `WINC_SOCK_SLAB_ALLOC_MODE` is defined to be 2 the sockets interface will use a main slab allocation for management tasks and then a slab per socket created. The management slab is created the same as the single slab from allocation mode 1, however as this slab does not contain any socket allocations it does not need to be sized to cope with the expect number of active sockets.

In addition to the management slab, when each socket is created it will allocate an additional slab dedicated solely to that socket. The size of this slab will be dictated by the buffer dimensions of the sockets.

##### Socket Memory Requirements

The memory required for each created socket is determined based on the size of the receive and transmit data buffers as well as the number of receive and transmit datagrams supported, plus some management overhead for the socket. Each type of allocation (receive/transmit data buffer or datagram structure) will be rounded to occupy a whole slab size.

For allocation mode 1, the memory for each type of allocation will be allocated from the single slab as a contiguous allocation, however the four types of allocation will not need to be contiguous, so the transmit buffer can be located separately from the receive buffer allocation.

For allocation mode 2, all four types of allocation are allocated as a single block from the provided heap.

Datagram allocations occupy approximately 8 + (32 \* number of datagrams) bytes.

    If the slab size is 512 bytes:

    A socket with a receive buffer of 1600, transmit buffer of 1300 and supporting up to 4 datagrams for both transmit and receive would require:

    2048 (1600 rounded to 512) + 1536 (1300 round to 512) + 512 (4 datagrams) + 512 (4 datagrams) = 4608 bytes

---
#### Socket Event Callback

A socket event callback of type [WINC_SOCKET_EVENT_CALLBACK](#AN_FUNC_API_WINC_SOCKET_EVENT_CALLBACK) may be registered with the socket API by calling `WINC_SockRegisterEventCallback`. The purpose of this callback is to provide low level socket events to the application. It is also possible to poll the Berkeley API to ascertain status without using the callback.

#### Creating Sockets

Sockets are created by calling the function [socket](#AN_FUNC_API_SOCKET).

``` c
/* Creating IPaddr TCP socket. */
int sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
```

``` c
/* Creating IPv6 TLS socket. */
int sockfd = socket(AF_INET6, SOCK_STREAM, IPPROTO_TLS);
```

``` c
/* Creating IPaddr UDP socket. */
int sockfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
```

Once created the WINCS02 device will need to allocate resources.

**Callback:** Completion of the creation process will be signalled via the callback using event `WINC_SOCKET_EVENT_OPEN`.

**Polled:** Completion of TCP/UDP client sockets will be signalled via [connect](#AN_FUNC_API_CONNECT), this will return -1 for error and the `errno` value `EINPROGRESS`. TCP server listening sockets can successfully [bind](#AN_FUNC_API_BIND) during completion, then [listen](#AN_FUNC_API_LISTEN) will return -1 with `errno` value `EAGAIN`. UDP server listening sockets will return -1 from [bind](#AN_FUNC_API_BIND) with a value of `EAGAIN` until complete.

Attempting to call another socket function before the socket creation process has completed will normally result in that call failing with `errno` value `ENOTSOCK`.

---
#### Server Listening Sockets

Once created a socket can be bound to a local endpoint to create a server listening socket. Multicast sockets are also bound to a local endpoint.

``` c
struct sockaddr_in addr;

addr.sin_family      = AF_INET;
addr.sin_port        = htons(80);
addr.sin_addr.s_addr = htonl(INADDR_ANY);

/* Bind IPv4 TCP socket to local port 80. */
bind(sockfd, (struct sockaddr*)&addr, sizeof(struct sockaddr_in))
```

``` c
struct sockaddr_in6 addr;

addr.sin_family      = AF_INET;
addr.sin_port        = htons(80);
memcpy(&addr.sin6_addr, &in6addr_any, sizeof(in6addr_any));

/* Bind IPv6 TCP socket to local port 80. */
bind(sockfd, (struct sockaddr*)&addr, sizeof(struct sockaddr_in))
```

If the socket supports TLS, the socket must be associated with a TLS context. The TLS function [WINC_CmdTLSC](#AN_FUNC_AT_TLS_TLSC) configures TLS contexts. The `optConf` configuration number will need to be passed to the socket via the [setsockopt](#AN_FUNC_API_SETSOCKOPT) function.

``` c
int tlsIndex;               /* Set to same value as WINC_CmdTLSC. */

setsockopt(sockfd, IPPROTO_TLS, TLS_CONF_IDX, &tlsIndex, sizeof(tlsIndex));
```

TCP server listening sockets will then need to be set to a listening state by calling [listen](#AN_FUNC_API_LISTEN). A backlog can be specified which sets the number of simultaneous sockets supported, the maximum supported is specified by `SOMAXCONN`.

> ***NOTE:*** The backlog value `0` means default which, to converse resources, will be a single socket.

``` c
listen(sockfd, 0);
```

**Callback:** Once a TCP socket has been configured for listening the event callback will receive the event `WINC_SOCKET_EVENT_LISTEN`. A UDP socket will generate this event in response to the earlier [bind](#AN_FUNC_API_BIND) request.

**Polled:** A TCP socket will return -1 and `errno` value `EAGAIN` until the [listen](#AN_FUNC_API_LISTEN) process has completed. A UDP socket is the same in response to the [bind](#AN_FUNC_API_BIND) call.

---
#### Client Sockets

If the socket supports TLS, the socket must be associated with a TLS context. The TLS API manages TLS contexts and creates context handles; the handle will need to be passed to the socket via the [setsockopt](#AN_FUNC_API_SETSOCKOPT) function after being converted to an index value by calling `WDRV_WINC_TLSCtxHandleToCfgIdx`.

``` c
int tlsIndex = WDRV_WINC_TLSCtxHandleToCfgIdx(tlsHandle);

setsockopt(sockfd, IPPROTO_TLS, TLS_CONF_IDX, &tlsIndex, sizeof(tlsIndex));
```

TCP sockets will then need to be connected to a remote endpoint by calling [connect](#AN_FUNC_API_CONNECT).

``` c
struct sockaddr_in addr;

addr.sin_family      = AF_INET;
addr.sin_port        = htons(80);
addr.sin_addr.s_addr = htonl(0xC0A80064);

/* Connect an IPv4 socket to 192.168.0.100:80. */
connect(sockfd, (struct sockaddr*)&addr, sizeof(sockaddr_in));
```

#### Multicast Sockets

Multicast sockets start like server listening sockets by being bound to a local endpoint. The socket then needs to be joined into the appropriate multicast group.

``` c
struct in_addr addr = htonl(0xE0000001U);
struct ip_mreqn group;

memcpy(&group.imr_multiaddr, &addr, sizeof(struct in_addr));
memcpy(&group.imr_address, &addr, sizeof(struct in_addr));

group.imr_ifindex = 0;

/* Join the IPv4 multicast group 224.0.0.1. */
setsockopt(sockfd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &group, sizeof(group));
```

``` c
struct in6_addr addr = {/* IPv6 multicast address*/}
struct ipv6_mreq group;

memcpy(&group.ipv6mr_multiaddr, &addr, sizeof(struct in6_addr));

group.ipv6mr_interface = 0;

/* Joining a IPv6 multicast. */
setsockopt(sockfd, IPPROTO_IP, IPV6_ADD_MEMBERSHIP, &group, sizeof(group));
```

---
#### Incoming Server Socket Connections

**Callback:** For TCP sockets a new incoming connection request is signalled via the callback event `WINC_SOCKET_EVENT_CONNECT_REQ`.

**Polled:** New connection requests will be signalled through the [poll](#AN_FUNC_API_POLL) function. Selecting the event `POLLIN` on a server listening socket will result in the `revent` value `POLLIN` being signalled.

``` c
struct pollfd fd;

fd.fd     = sockh;
fd.events = POLLIN;

if (-1 == poll(&fd, 1, 0))
{
    printf("error\n");
}
else if (0 != (fd.revents & POLLIN))
{
    union sockaddr_union sockAddr;
    socklen_t sockAddrLen = sizeof(union sockaddr_union);
    int newSockh;

    newSockh = accept(sockh, (struct sockaddr*)&sockAddr, &sockAddrLen)
}
```

In response to a connection attempt the application may accept the connection by calling [accept](#AN_FUNC_API_ACCEPT).

``` c
struct sockaddr_in addr;
socklen_t addrLen = sizeof(struct sockaddr_in);

/* Accept an incoming IPv4 connection request. */
new_sockfd = accept(sockfd, (struct sockaddr*)&addr, &addrLen);
```

``` c
struct sockaddr_in6 addr;
socklen_t addrLen = sizeof(struct sockaddr_in6);

/* Accept an incoming IPv6 connection request. */
new_sockfd = accept(sockfd, (struct sockaddr*)&addr, &addrLen);
```

---
#### Client Socket Connections

**Callback:** Completion of TCP client socket connections are indicated be reception of the `WINC_SOCKET_EVENT_CONNECT` event. If TLS has been configured on the socket a second event, `WINC_SOCKET_EVENT_TLS_CONNECT` will indicate that TLS has also connected and that data is ready to flow.

**Polled:** While connections are in progress [connect](#AN_FUNC_API_CONNECT) will return -1 and `errno` value `EINPROGRESS`. Calling [poll](#AN_FUNC_API_POLL) with event `POLLOUT` will signal the `revent` for `POLLOUT` when connected.

``` c
struct pollfd fd;

fd.fd     = sockh;
fd.events = POLLOUT;

if (-1 == poll(&fd, 1, 0))
{
    printf("error\n");
}
else if (0 != (fd.revents & POLLOUT))
{
    printf("socket connected\n");
}
```

---
#### Sending Data

To send data the application can call either [send](#AN_FUNC_API_SEND) for streaming sockets (TCP/TLS) or [sendto](#AN_FUNC_API_SENDTO) for datagram sockets (UDP).

``` c
/* Send data via TCP socket. */
send(sockfd, dataPtr, dataLength, 0);
```

``` c
struct sockaddr_in      addr

addr.sin_family      = AF_INET;
addr.sin_port        = htons(1000);
addr.sin_addr.s_addr = htonl(0xC0A80064);

/* Send data via UDP socket to 192.168.0.100:1000. */
sendto(sockfd, dataPtr, dataLength, 0, (struct sockaddr*)&addr, sizeof(struct sockaddr_in));
```

If the socket is available for sending the call to [send](#AN_FUNC_API_SEND) or [sendto](#AN_FUNC_API_SENDTO) will return the number of byte written. If the socket is not available the call will return -1 with `errno` value `EWOULDBLOCK` / `EAGAIN`.

**Callback:** There is an `WINC_SOCKET_EVENT_SEND` event delivered to the event callback, however this does not correspond directly to the calling of [send](#AN_FUNC_API_SEND) or [sendto](#AN_FUNC_API_SENDTO). The event corresponds to the low level sending of socket data to the WINCS02. Calling [send](#AN_FUNC_API_SEND) or [sendto](#AN_FUNC_API_SENDTO) places the application data into an internal buffer within the WINCS02 driver, the driver then chooses when and how to deliver this data to the WINCS02 device.

**Polled:** The ability to send data through a socket will be signalled through [poll](#AN_FUNC_API_POLL) event `POLLOUT`. When the `revent` for the socket signals `POLLOUT` the application may send data.

``` c
struct pollfd fd;

fd.fd     = sockh;
fd.events = POLLOUT;

if (-1 == poll(&fd, 1, 0))
{
    printf("error\n");
}
else if (0 != (fd.revents & POLLOUT))
{
    send(sockh, buffer, numBytes, 0);
}
```

---
#### Receiving Data

To receive data the application can call either [recv](#AN_FUNC_API_RECV) for streaming sockets (TCP/TLS) or [recvfrom](#AN_FUNC_API_RECVFROM) for datagram sockets (UDP).

``` c
uint8_t buffer[128];

/* Receive data from a TCP socket. */
recv(sockfd, buffer, sizeof(buffer), 0);
```

``` c
uint8_t buffer[128];
struct sockaddr_in addr;
socklen_t fromLen = sizeof(struct sockaddr_in);

/* Receive data from a UDP socket. */
recvfrom(sockfd, buffer, sizeof(buffer), 0, (struct sockaddr*)&addr, &fromLen);
```

**Callback:** There is an `WINC_SOCKET_EVENT_RECV` event delivered to the event callback, however this does not correspond directly to data being available through [recv](#AN_FUNC_API_RECV) or [recvfrom](#AN_FUNC_API_RECVFROM). The event corresponds to the low level reception of data from the WINCS02. When data is received from the WINCS02 device it is placed in an internal buffer within the WINCS02 driver, the driver then chooses when and how to deliver this data to the application.

**Polled:** The ability to receive data from a socket will be signalled through [poll](#AN_FUNC_API_POLL) event `POLLIN`. When the `revent` for the socket signals `POLLIN` the application may receive data.

``` c
struct pollfd fd;

fd.fd     = sockh;
fd.events = POLLIN;

if (-1 == poll(&fd, 1, 0))
{
    printf("error\n");
}
else if (0 != (fd.revents & POLLIN))
{
    recv(sockh, buffer, numBytes, 0);
}
```

---
#### TCP Socket Termination

Remote socket termination can be detected when attempting to send or receive data, or when polling using [poll](#AN_FUNC_API_POLL).

[recv](#AN_FUNC_API_RECV): When a stream socket peer has performed an orderly shutdown, the return value of [recv](#AN_FUNC_API_RECV) will be `0`, the traditional 'end-of-file' value.

[send](#AN_FUNC_API_SEND): Attempting to send on a terminated socket will result in a return value of -1 and the `errno` value of `ENOTCONN`.

[poll](#AN_FUNC_API_POLL): The value `POLLHUP` will be signalled in `revents` when a connection is terminated. `POLLIN` can be used to determine if the socket has remaining data to receive.

``` c
struct pollfd fd;

fd.fd     = sockh;
fd.events = POLLIN|POLLOUT;

if (-1 == poll(&fd, 1, 0))
{
    printf("error\n");
}
else if (0 != (fd.revents & POLLHUP))
{
    printf("socket disconnected\n");

    if (0 == (fd.revents & POLLIN))
    {
        /* No pending data to receive, socket can be closed. */
    }
}
```

---
#### Closing Sockets

To close a socket the application should use the function [shutdown](#AN_FUNC_API_SHUTDOWN).

#### DNS Resolution.

This API includes the function [getaddrinfo](#AN_FUNC_API_GETADDRINFO) which can be used to resolve hostnames. Resolved names result in a list of `struct addrinfo` structures which are dynamically created, therefore the application must call [freeaddrinfo](#AN_FUNC_API_FREEADDRINFO) when finished with the results.

For IPv6 AAAA record resolution a hints structure can be included.

``` c
struct addrinfo *pAddrInfo;
int result;

result = getaddrinfo("www.example.com", NULL, NULL, &pAddrInfo);

if (0 == result)
{
    /* Result is available. */
}
else if (EAI_AGAIN == result)
{
    /* Result is not available yet, try again. */
}
else
{
    /* An error occurred. */
}

if (NULL != pAddrInfo)
{
    /* Clean up allocation results structures. */
    freeaddrinfo(pAddrInfo);
}
```

``` c
struct addrinfo hints;
struct addrinfo *pAddrInfo;
int result;

/* Indicate IPv6 AAAA records are required. */
memset(&hints, 0, sizeof(hints));
hints.ai_family = AF_INET6;

result = getaddrinfo("www.example.com", NULL, &hints, &pAddrInfo);
```

---
### API Reference

#### WINC_SOCKET_EVENT

##### Description

Socket event callback types.

``` c
typedef enum
{
    WINC_SOCKET_EVENT_OPEN,
    WINC_SOCKET_EVENT_LISTEN,
    WINC_SOCKET_EVENT_CONNECT_REQ,
    WINC_SOCKET_EVENT_CONNECT,
    WINC_SOCKET_EVENT_SEND,
    WINC_SOCKET_EVENT_RECV,
    WINC_SOCKET_EVENT_CLOSE,
    WINC_SOCKET_EVENT_TLS_CONNECT,
    WINC_SOCKET_EVENT_ERROR
} WINC_SOCKET_EVENT;
```

##### Members

| Member | Description |
|----|----|
| WINC_SOCKET_EVENT_OPEN | Socket create/open has completed. |
| WINC_SOCKET_EVENT_LISTEN | Socket listen on local endpoint completed. |
| WINC_SOCKET_EVENT_CONNECT_REQ | Connection request received. |
| WINC_SOCKET_EVENT_CONNECT | Connect to remove endpoint completed. |
| WINC_SOCKET_EVENT_SEND | Data send operation completed. |
| WINC_SOCKET_EVENT_RECV | Data receive operation completed. |
| WINC_SOCKET_EVENT_CLOSE | Socket close completed. |
| WINC_SOCKET_EVENT_TLS_CONNECT | TLS connection to remote endpoint completed. |
| WINC_SOCKET_EVENT_ERROR | An error has occurred. |

##### Remarks

None.

---
#### WINC_SOCKET_STATUS

##### Description

Socket status types.

``` c
typedef enum
{
    WINC_SOCKET_STATUS_OK,
    WINC_SOCKET_STATUS_ERROR
} WINC_SOCKET_STATUS;
```

##### Members

| Member                   | Description             |
|--------------------------|-------------------------|
| WINC_SOCKET_STATUS_OK    | The status is OK.       |
| WINC_SOCKET_STATUS_ERROR | The status is an error. |

##### Remarks

None.

---
<a id="AN_FUNC_API_WINC_SOCKET_INIT_TYPE"></a>
#### WINC_SOCKET_INIT_TYPE

##### Description

Socket module initialisation structure.

``` c
typedef struct
{
    void*           (*pfMemAlloc)(size_t size);
    void            (*pfMemFree)(void *pData);
    size_t          slabSize;
    int8_t          numSlabs;
} WINC_SOCKET_INIT_TYPE;
```

##### Members

| Member     | Description                                   |
|------------|-----------------------------------------------|
| pfMemAlloc | Function pointer for allocating memory.       |
| pfMemFree  | Function pointer for freeing memory.          |
| slabSize   | Size, in bytes, of a single slab allocations. |
| numSlabs   | Number of slabs in main allocation.           |

##### Remarks

None.

---
<a id="AN_FUNC_API_WINC_SOCKET_EVENT_CALLBACK"></a>
#### WINC_SOCKET_EVENT_CALLBACK

##### Description

Socket event callback function type.

``` c
typedef void (*WINC_SOCKET_EVENT_CALLBACK)
(
    uintptr_t context,
    int socket,
    WINC_SOCKET_EVENT event,
    WINC_SOCKET_STATUS status
);
```

##### Parameters

| Parameter | Type               | Description                             |
|-----------|--------------------|-----------------------------------------|
| context   | uintptr_t          | User supplied callback context.         |
| socket    | int                | Socket handle.                          |
| event     | WINC_SOCKET_EVENT  | Socket event, see `WINC_SOCKET_EVENT`.  |
| status    | WINC_SOCKET_STATUS | Event status, see `WINC_SOCKET_STATUS`. |

##### Returns

None.

##### Remarks

None.

---
<a id="AN_FUNC_API_WINC_SOCKDEINIT"></a>
#### WINC_SockDeinit

##### Description

De-initialise the socket module.

``` c
bool WINC_SockDeinit(WINC_DEVICE_HANDLE devHandle)
```

##### Parameters

| Parameter | Type               | Description        |
|-----------|--------------------|--------------------|
| devHandle | WINC_DEVICE_HANDLE | WINC device handle |

##### Returns

true or false indicating success or failure

##### Remarks

None.

---
<a id="AN_FUNC_API_WINC_SOCKINIT"></a>
#### WINC_SockInit

##### Description

Initialise the socket module.

``` c
bool WINC_SockInit(WINC_DEVICE_HANDLE devHandle, WINC_SOCKET_INIT_TYPE *pInitData)
```

##### Parameters

| Parameter | Type                  | Description                    |
|-----------|-----------------------|--------------------------------|
| devHandle | WINC_DEVICE_HANDLE    | WINC device handle             |
| pInitData | WINC_SOCKET_INIT_TYPE | Pointer to initialisation data |

##### Returns

true or false indicating success or failure

##### Remarks

If `pInitData` is not `NULL` this function initialises the socket interface, if the pointer is `NULL` this function will reset an already initialised socket interface back to it’s initial state.

---
<a id="AN_FUNC_API_ACCEPT"></a>
#### accept

##### Description

Accept a connection on a socket.

``` c
int accept(int fd, struct sockaddr *addr, socklen_t *len)
```

##### Parameters

| Parameter | Type | Description |
|----|----|----|
| fd | int | Socket file descriptor. |
| addr | struct sockaddr\* | Pointer to a structure to filled in with the address of the peer socket. |
| len | socklen_t\* | Length of address structure. |

##### Returns

Socket file descriptor or -1 for error (errno set).

##### Remarks

| errno | Description |
|----|----|
| EBADF | The argument `fd` is not a valid file descriptor. |
| ENOMEM | Insufficient memory is available. |
| EWOULDBLOCK | The socket is marked nonblocking and no connections are present to be accepted. |

---
<a id="AN_FUNC_API_BIND"></a>
#### bind

##### Description

Bind a name to a socket.

``` c
int bind(int fd, const struct sockaddr *addr, socklen_t len)
```

##### Parameters

| Parameter | Type              | Description                |
|-----------|-------------------|----------------------------|
| fd        | int               | Socket file descriptor.    |
| addr      | struct sockaddr\* | Pointer to socket address. |
| len       | socklen_t         | Length of socket address.  |

##### Returns

- 0 - Success.

- -1 - Error, `errno` set.

##### Remarks

| errno | Description |
|----|----|
| EFAULT | System fault. |
| EAFNOSUPPORT | The implementation does not support the specified address family. |
| ENOMEM | Insufficient memory is available. |
| EBADMSG | Bad message. |
| EAGAIN | The socket is nonblocking, and the binding cannot be completed immediately. |

---
<a id="AN_FUNC_API_CONNECT"></a>
#### connect

##### Description

Initiate a connection on a socket.

``` c
int connect(int fd, const struct sockaddr *addr, socklen_t len)
```

##### Parameters

| Parameter | Type              | Description                |
|-----------|-------------------|----------------------------|
| fd        | int               | Socket file descriptor.    |
| addr      | struct sockaddr\* | Pointer to socket address. |
| len       | socklen_t         | Length of socket address.  |

##### Returns

- 0 - Success.

- -1 - Error, `errno` set.

##### Remarks

| errno | Description |
|----|----|
| EFAULT | System fault. |
| ENOTSOCK | The file descriptor `fd` does not refer to a socket. |
| EAFNOSUPPORT | The implementation does not support the specified address family. |
| EAGAIN | The socket is nonblocking, and the connection cannot be completed immediately. |
| ENOMEM | Insufficient memory is available. |
| EBADMSG | Bad message. |
| EINPROGRESS | The socket is nonblocking and the connection cannot be completed immediately.\<br\>It is possible to poll for completion by selecting the socket for writing. After poll indicates writability. |
| EISCONN | The socket is already connected. |

---
#### inet_ntop

##### Description

Convert IPv4 and IPv6 addresses from binary to text form.

``` c
const char *inet_ntop(int af, const void *a0, char *s, socklen_t l)
```

##### Parameters

| Parameter | Type      | Description                                     |
|-----------|-----------|-------------------------------------------------|
| af        | int       | Address family, either `AF_INET` or `AF_INET6`. |
| a0        | void\*    | Pointer to IP address in network byte order.    |
| s         | char\*    | Pointer to string buffer to output to.          |
| l         | socklen_t | Size of buffer supplied.                        |

##### Returns

Pointer to converted string within supplied buffer or 0 for error (errno set).

##### Remarks

| errno | Description |
|----|----|
| EAFNOSUPPORT | `af` was not a valid address family. |
| ENOSPC | The converted address string would exceed the size given by size. |

---
#### inet_pton

##### Description

Convert IPv4 and IPv6 addresses from text to binary form.

``` c
int inet_pton(int af, const char *s, void *a0)
```

##### Parameters

| Parameter | Type   | Description                                     |
|-----------|--------|-------------------------------------------------|
| af        | int    | Address family, either `AF_INET` or `AF_INET6`. |
| s         | char\* | Pointer to input IP address string.             |
| a0        | void\* | Pointer to output binary form IP address.       |

##### Returns

- -1 - Error, `errno` is set.

- 0 - No valid IP address string found.

- 1 - Success.

##### Remarks

| errno        | Description                          |
|--------------|--------------------------------------|
| EAFNOSUPPORT | `af` was not a valid address family. |

---
<a id="AN_FUNC_API_LISTEN"></a>
#### listen

##### Description

Listen for connections on a socket.

``` c
int listen(int fd, int backlog)
```

##### Parameters

| Parameter | Type | Description                            |
|-----------|------|----------------------------------------|
| fd        | int  | Socket file descriptor.                |
| backlog   | int  | Maximum number of pending connections. |

##### Returns

- 0 - Success.

- -1 - Error, `errno` set.

##### Remarks

| errno | Description |
|----|----|
| EADDRINUSE | The referred to by `fd` is not bound to a local port. |
| EBADF | The argument `fd` is not a valid file descriptor. |
| ENOTSOCK | The file descriptor `fd` does not refer to a socket. |
| EOPNOTSUPP | The socket is not of a type that supports the listen() operation. |
| EAGAIN | The socket is nonblocking, and the listening cannot be completed immediately. |

---
<a id="AN_FUNC_API_POLL"></a>
#### poll

##### Description

Wait for some event on a file descriptor.

``` c
int poll(struct pollfd *fds, nfds_t nfds, int timeout)
```

##### Parameters

| Parameter | Type | Description |
|----|----|----|
| fds | struct pollfd\* | Set of file descriptors to be monitored. |
| nfds | nfds_t | Number of items in the fds array. |
| timeout | int | Specifies the number of milliseconds to block block waiting for a file descriptor to become ready.\<br\>Must be 0. |

##### Returns

On success, `poll()` returns a nonnegative value which is the number of elements in the pollfds whose revents fields have been set to a nonzero value (indicating an event or an error).

A return value of zero indicates that the system call timed out before any file descriptors became ready.

On error, -1 is returned, and `errno` is set to indicate the error.

##### Remarks

| errno  | Description                                             |
|--------|---------------------------------------------------------|
| EFAULT | System fault.                                           |
| EINVAL | The nfds value exceeds the WINC_SOCK_NUM_SOCKETS value. |

| fds events/revents | Description |
|----|----|
| POLLIN | There is data to read. |
| POLLOUT | Writing is now possible. |
| POLLHUP | Hang up (only returned in revents; ignored in events).\<br\>Subsequent reads from the channel will return 0 (end of file) only after all outstanding data in the channel has been consumed. |
| POLLNVAL | Invalid request: fd not open (only returned in revents; ignored in events). |

---
<a id="AN_FUNC_API_RECV"></a>
#### recv

##### Description

Receive a message from a socket.

``` c
ssize_t recv(int fd, void *buf, size_t len, int flags)
```

##### Parameters

| Parameter | Type   | Description                              |
|-----------|--------|------------------------------------------|
| fd        | int    | Socket file descriptor.                  |
| buf       | void\* | Pointer to buffer to receive data.       |
| len       | size_t | Length of data to receive.               |
| flags     | int    | Option for reception, currently ignored. |

##### Returns

The number of bytes received or -1 for error, see `errno`. If the return value is 0, the socket has performed an orderly shutdown.

##### Remarks

| errno | Description |
|----|----|
| EBADF | The argument `fd` is not a valid file descriptor. |
| EFAULT | System fault. |
| ENOTSOCK | The file descriptor `fd` does not refer to a socket. |
| EWOULDBLOCK | The socket is marked nonblocking and the receive operation would block. |

---
<a id="AN_FUNC_API_RECVFROM"></a>
#### recvfrom

##### Description

Receive a message from a socket.

``` c
ssize_t recvfrom(int fd, void *buf, size_t len, int flags, struct sockaddr *addr, socklen_t *alen)
```

##### Parameters

| Parameter | Type | Description |
|----|----|----|
| fd | int | Socket file descriptor. |
| buf | void\* | Pointer to buffer to receive data. |
| len | size_t | Length of data to receive. |
| flags | int | Option for reception, currently ignored. |
| addr | struct sockaddr\* | Pointer to a structure to receive the peer address. |
| alen | ocklen_t\* | Pointer to length of address structure. |

##### Returns

The number of bytes received or -1 for error, see `errno`. If the return value is 0, the socket has performed an orderly shutdown.

##### Remarks

| errno | Description |
|----|----|
| EBADF | The argument `fd` is not a valid file descriptor. |
| EFAULT | System fault. |
| ENOTSOCK | The file descriptor `fd` does not refer to a socket. |
| EWOULDBLOCK | The socket is marked nonblocking and the receive operation would block. |

---
<a id="AN_FUNC_API_SEND"></a>
#### send

##### Description

Send a message on a socket.

``` c
ssize_t send(int fd, const void *buf, size_t len, int flags)
```

##### Parameters

| Parameter | Type   | Description                                 |
|-----------|--------|---------------------------------------------|
| fd        | int    | Socket file descriptor.                     |
| buf       | void\* | Pointer to buffer containing data to send.  |
| len       | size_t | Length of data to send.                     |
| flags     | int    | Option for transmission, currently ignored. |

##### Returns

The number of bytes sent or -1 for error, see `errno`.

##### Remarks

| errno | Description |
|----|----|
| EBADF | The argument `fd` is not a valid file descriptor. |
| EFAULT | System fault. |
| ENOTSOCK | The file descriptor `fd` does not refer to a socket. |
| EWOULDBLOCK | The socket is marked nonblocking and the send operation would block. |
| ENOMEM | Insufficient memory is available. |
| EDESTADDRREQ | The socket is not connection-mode, and no peer address is set. |
| ENOTCONN | The socket is not connected, and no target has been given. |

---
<a id="AN_FUNC_API_SENDTO"></a>
#### sendto

##### Description

Send a message on a socket.

``` c
ssize_t sendto(int fd, const void *buf, size_t len, int flags, const struct sockaddr *addr, socklen_t alen)
```

##### Parameters

| Parameter | Type              | Description                                 |
|-----------|-------------------|---------------------------------------------|
| fd        | int               | Socket file descriptor.                     |
| buf       | void\*            | Pointer to buffer containing data to send.  |
| len       | size_t            | Length of data to send.                     |
| flags     | int               | Option for transmission, currently ignored. |
| addr      | struct sockaddr\* | Pointer to address structure.               |
| alen      | socklen_t         | Length of address structure.                |

##### Returns

The number of bytes sent or -1 for error, see `errno`.

##### Remarks

| errno | Description |
|----|----|
| EBADF | The argument `fd` is not a valid file descriptor. |
| EFAULT | System fault. |
| ENOTSOCK | The file descriptor `fd` does not refer to a socket. |
| EWOULDBLOCK | The socket is marked nonblocking and the send operation would block. |
| ENOMEM | Insufficient memory is available. |
| EMSGSIZE | The argument data is too long to pass atomically through the underlying protocol. |
| EDESTADDRREQ | The socket is not connection-mode, and no peer address is set. |
| ENOTCONN | The socket is not connected, and no target has been given. |

---
<a id="AN_FUNC_API_SETSOCKOPT"></a>
#### setsockopt

##### Description

Set options on sockets.

``` c
int setsockopt(int fd, int level, int optname, const void *optval, socklen_t optlen)
```

##### Parameters

| Parameter | Type      | Description             |
|-----------|-----------|-------------------------|
| fd        | int       | Socket file descriptor. |
| level     | int       | Option level.           |
| optname   | int       | Option name.            |
| optval    | void\*    | Option value.           |
| optlen    | socklen_t | Length of option value. |

##### Returns

- 0 - Success.

- -1 - Error, `errno` set.

##### Remarks

| errno       | Description                                       |
|-------------|---------------------------------------------------|
| EBADF       | The argument `fd` is not a valid file descriptor. |
| ENOPROTOOPT | The option is unknown at the level indicated.     |
| EINVAL      | `optlen` invalid.                                 |
| ENOMEM      | Insufficient memory is available.                 |
| EBADMSG     | Bad message.                                      |

##### Socket options IP:

IP supports some protocol-specific socket options that can be set with [setsockopt](#AN_FUNC_API_SETSOCKOPT). The socket option level for IP is `IPPROTO_IP`. A boolean integer flag is zero when it is false, otherwise true. Unless otherwise noted, `optval` is a pointer to an int.

When an invalid socket option is specified, [setsockopt](#AN_FUNC_API_SETSOCKOPT) fail with the error `ENOPROTOOPT`.

**IP_TOS:** Set or receive the Type-Of-Service (TOS) field that is sent with every IP packet originating from this socket. It is used to prioritize packets on the network. TOS is an int. There are some standard TOS flags defined: `IPTOS_LOWDELAY` to minimize delays for interactive traffic, `IPTOS_THROUGHPUT` to optimize throughput, `IPTOS_RELIABILITY` to optimize for reliability. At most one of these TOS values can be specified. Other bits are invalid and shall be cleared.

**IP_ADD_MEMBERSHIP:** Join a multicast group. Argument is an `ip_mreqn` structure.

``` c
struct ip_mreqn {
    struct in_addr imr_multiaddr;
    struct in_addr imr_address;
    int            imr_ifindex;
};
```

The structure `imr_multiaddr` contains the address of the multicast group the application wants to join or leave. It must be a valid multicast address (or [setsockopt](#AN_FUNC_API_SETSOCKOPT) fails with the error `EINVAL`).

**IPV6_ADD_MEMBERSHIP:** Control membership in multicast groups. Argument is a pointer to a `struct ipv6_mreq`.

##### Socket options SOL_SOCKET:

The socket options listed below can be set by using [setsockopt](#AN_FUNC_API_SETSOCKOPT) with the socket level set to `SOL_SOCKET` for all sockets.

**SO_ASYNC_MODE:** Set the asynchronous read mode. The argument is a integer. A value of 0 turns this mode off, 1 enables a simple protocol and 2 enables an acknowledged protocol.

**SO_KEEPALIVE:** Enable sending of keep-alive messages on connection-oriented sockets. Expects an integer boolean flag.

**SO_LINGER:** Sets the SO_LINGER option. The argument is a integer.

**SO_RCVBUF:** Sets the maximum socket receive buffer in bytes.

**SO_SNDBUF:** Sets the maximum socket send buffer in bytes.

##### Socket options IPPROTO_TCP:

To set a TCP socket option, call [setsockopt](#AN_FUNC_API_SETSOCKOPT) to write the option with the option level argument set to `IPPROTO_TCP`.

**TCP_NODELAY:** If set, disable the Nagle algorithm. This means that segments are always sent as soon as possible, even if there is only a small amount of data. When not set, data is buffered until there is a sufficient amount to send out, thereby avoiding the frequent sending of small packets, which results in poor utilization of the network.

##### Socket options IPPROTO_TLS:

To set a TCP(TLS) socket option, call [setsockopt](#AN_FUNC_API_SETSOCKOPT) to write the option with the option level argument set to `IPPROTO_TLS`.

**TLS_CONF_IDX:** Sets the TLS configuration index.

---
<a id="AN_FUNC_API_SHUTDOWN"></a>
#### shutdown

##### Description

Shut down part of a full-duplex connection.

``` c
int shutdown(int fd, int how)
```

##### Parameters

| Parameter | Type | Description                          |
|-----------|------|--------------------------------------|
| fd        | int  | Socket file descriptor.              |
| how       | int  | Shutdown flags, must be `SHUT_RDWR`. |

##### Returns

- 0 - Success.

- -1 - Error, `errno` set.

##### Remarks

| errno | Description |
|----|----|
| EBADF | `fd` is not a valid file descriptor. |
| ENOTSOCK | The file descriptor `fd` does not refer to a socket. |
| ENOMEM | Insufficient memory is available. The socket cannot be created until sufficient resources are freed. |
| EBADMSG | Bad message. |

---
<a id="AN_FUNC_API_SOCKET"></a>
#### socket

##### Description

Create an endpoint for communication.

``` c
int socket(int domain, int type, int protocol)
```

##### Parameters

| Parameter | Type | Description                                                |
|-----------|------|------------------------------------------------------------|
| domain    | int  | Communication domain, must be `AF_INET` or `AF_INET6`.     |
| type      | int  | Socket type, must be `SOCK_STREAM` or `SOCK_DGRAM`.        |
| protocol  | int  | Specific socket protocol, should be zero or `IPPROTO_TLS`. |

##### Returns

Socket file descriptor or -1 for error (`errno` set).

##### Remarks

| errno | Description |
|----|----|
| EAFNOSUPPORT | The implementation does not support the specified address family. |
| EINVAL | Unknown protocol, or protocol family not available. |
| EPROTONOSUPPORT | The protocol type or the specified protocol is not supported within this domain. |
| EFAULT | System fault |
| ENFILE | The system-wide limit on the total number of open files has been reached. |
| ENOMEM | Insufficient memory is available. The socket cannot be created until sufficient resources are freed. |
| EBADMSG | Bad message. |

---
<a id="AN_FUNC_API_FREEADDRINFO"></a>
#### freeaddrinfo

##### Description

Frees the memory allocated by [getaddrinfo](#AN_FUNC_API_GETADDRINFO).

``` c
void freeaddrinfo(struct addrinfo *p)
```

##### Parameters

| Parameter | Type | Description |
|----|----|----|
| p | struct addrinfo\* | Pointer to address linked list returned by `getaddrinfo()`. |

##### Returns

None.

##### Remarks

None.

---
<a id="AN_FUNC_API_GETADDRINFO"></a>
#### getaddrinfo

##### Description

Network address and service translation.

``` c
int getaddrinfo(const char *host, const char *serv, const struct addrinfo *hint, struct addrinfo **res)
```

##### Parameters

| Parameter | Type | Description |
|----|----|----|
| host | char\* | Pointer to host to translate. |
| serv | char\* | Pointer to service to translate, currently ignored. |
| hint | struct addrinfo\* | Hint to affect the translation. |
| res | struct addrinfo\* | Pointer to results pointer. |

##### Returns

| value | Description |
|----|----|
| EAI_NONAME | The node or service is not known. |
| EAI_AGAIN | The name server returned a temporary failure indication. Try again later. |
| EAI_SYSTEM | Other system error; `errno` is set to indicate the error. |
| EAI_FAMILY | The requested address family is not supported. |
| EAI_MEMORY | Out of memory. |
| EAI_SERVICE | The requested service is not available for the requested socket type. |

##### Remarks

| errno   | Description   |
|---------|---------------|
| EFAULT  | System fault. |
| EBADMSG | Bad message.  |

The [getaddrinfo](#AN_FUNC_API_GETADDRINFO) function allocates and initializes a linked list of `addrinfo` structures, one for each network address that matches node and service, subject to any restrictions imposed by hints, and returns a pointer to the start of the list in `res`. The items in the linked list are linked by the `ai_next` field.

The [freeaddrinfo](#AN_FUNC_API_FREEADDRINFO) function frees the memory that was allocated for the dynamically allocated linked list `res`.

---
#### getpeername

##### Description

Returns the address of the peer connected to the socket fd.

``` c
int getpeername(int fd, struct sockaddr *addr, socklen_t *addrlen)
```

##### Parameters

| Parameter | Type        | Description                   |
|-----------|-------------|-------------------------------|
| fd        | int         | Socket file descriptor.       |
| addr      | sockaddr\*  | Pointer to address structure. |
| addrlen   | socklen_t\* | Length of address structure.  |

##### Returns

On success, zero is returned.

On error, -1 is returned, and `errno` is set to indicate the error.

##### Remarks

| errno    | Description                                                |
|----------|------------------------------------------------------------|
| EFAULT   | System fault.                                              |
| EINVAL   | addrlen is invalid (e.g., is negative).                    |
| ENOTSOCK | The file descriptor fd does not refer to a socket.         |
| ENOTCONN | The socket is not connected, and no target has been given. |

---
#### getsockname

##### Description

Returns the current address to which the socket fd is bound.

``` c
int getsockname(int fd, struct sockaddr *addr, socklen_t *addrlen)
```

##### Parameters

| Parameter | Type        | Description                   |
|-----------|-------------|-------------------------------|
| fd        | int         | Socket file descriptor.       |
| addr      | sockaddr\*  | Pointer to address structure. |
| addrlen   | socklen_t\* | Length of address structure.  |

##### Returns

On success, zero is returned.

On error, -1 is returned, and `errno` is set to indicate the error.

##### Remarks

| errno    | Description                                                |
|----------|------------------------------------------------------------|
| EFAULT   | System fault.                                              |
| EINVAL   | addrlen is invalid (e.g., is negative).                    |
| ENOTSOCK | The file descriptor fd does not refer to a socket.         |
| ENOTCONN | The socket is not connected, and no target has been given. |

---
#### htonl

##### Description

Convert 32-bit value from host to network byte order.

``` c
uint32_t htonl(uint32_t n)
```

##### Parameters

| Parameter | Type     | Description       |
|-----------|----------|-------------------|
| n         | uint32_t | Value to convert. |

##### Returns

Converted value.

##### Remarks

None.

---
#### htons

##### Description

Convert 16-bit value from host to network byte order.

``` c
uint16_t htons(uint16_t n)
```

##### Parameters

| Parameter | Type     | Description       |
|-----------|----------|-------------------|
| n         | uint16_t | Value to convert. |

##### Returns

Converted value.

##### Remarks

None.

---
#### ntohl

##### Description

Convert 32-bit value from network to host byte order.

``` c
uint32_t ntohl(uint32_t n)
```

##### Parameters

| Parameter | Type     | Description       |
|-----------|----------|-------------------|
| n         | uint32_t | Value to convert. |

##### Returns

Converted value.

##### Remarks

None.

---
#### ntohs

##### Description

Convert 16-bit value from network to host byte order.

``` c
uint16_t ntohs(uint16_t n)
```

##### Parameters

| Parameter | Type     | Description       |
|-----------|----------|-------------------|
| n         | uint16_t | Value to convert. |

##### Returns

Converted value.

##### Remarks

None.

---
---
### Examples

These are examples of using the Berkeley sockets API.

- TCP Client

- TCP Server

- UDP Client

- UDP Server

- DNS lookup

---
#### DNS Lookup

``` c
#include <string.h>

#define BSOCK_GET_ADDR_MAX_HOSTNAME_SZ      (256+1)

typedef enum
{
    MODULE_STATE_INIT,
    MODULE_STATE_WAIT,
    MODULE_STATE_END,
    MODULE_STATE_ERROR,
} MODULE_STATE;

typedef struct
{
    sa_family_t     sin_family;
    char            hostName[BSOCK_GET_ADDR_MAX_HOSTNAME_SZ];
} BSOCK_GET_ADDR_INIT_TYPE;

static MODULE_STATE                 state;
static BSOCK_GET_ADDR_INIT_TYPE     initData = {0};
static struct addrinfo              *pAddrInfo;
static struct addrinfo              *pHints, hints;

void bsock_get_addr_init(void *pInitData)
{
    if (NULL != pInitData)
    {
        memcpy(&initData, pInitData, sizeof(BSOCK_GET_ADDR_INIT_TYPE));
    }

    state = MODULE_STATE_INIT;
}

void bsock_get_addr_run(void)
{
    switch (state)
    {
        case MODULE_STATE_INIT:
        {
            int result;

            if (AF_INET == initData.sin_family)
            {
                memset(&hints, 0, sizeof(hints));
                hints.ai_family = AF_INET;
                pHints = &hints;
            }
            else if (AF_INET6 == initData.sin_family)
            {
                memset(&hints, 0, sizeof(hints));
                hints.ai_family = AF_INET6;
                pHints = &hints;
            }
            else if (AF_UNSPEC == initData.sin_family)
            {
                pHints = NULL;
            }
            else
            {
                printf("invalid address family %d\n", initData.sin_family);
                state = MODULE_STATE_ERROR;
            }

            pAddrInfo = NULL;

            errno = 0;
            result = getaddrinfo(initData.hostName, NULL, pHints, &pAddrInfo);

            printf("getaddrinfo = %d (%d)\n", result, errno);

            if (0 == result)
            {
                printf("result found\n");

                state = MODULE_STATE_END;
            }
            else if (EAI_AGAIN == result)
            {
                printf("result pending\n");
                state = MODULE_STATE_WAIT;
            }
            else
            {
                printf("result error\n");

                state = MODULE_STATE_ERROR;
            }

            break;
        }

        case MODULE_STATE_WAIT:
        {
            int result;

            pAddrInfo = NULL;

            errno = 0;
            result = getaddrinfo(initData.hostName, NULL, pHints, &pAddrInfo);

            printf("getaddrinfo = %d (%d)\n", result, errno);

            if (0 == result)
            {
                printf("result found\n");

                state = MODULE_STATE_END;
            }
            else if (EAI_AGAIN != result)
            {
                printf("result error\n");

                state = MODULE_STATE_ERROR;
            }

            break;
        }

        case MODULE_STATE_END:
        {
            if (NULL != pAddrInfo)
            {
                struct addrinfo *pRes = pAddrInfo;

                while (NULL != pRes)
                {
                    if (NULL != pRes->ai_addr)
                    {
                        char ipStr[64];
                        union sockaddr_union *pAddr = (union sockaddr_union*)pRes->ai_addr;

                        if (AF_INET == pAddr->sin_family)
                        {
                            inet_ntop(pAddr->sin_family, &pAddr->in4.sin_addr, ipStr, sizeof(ipStr));
                        }
                        else if (AF_INET6 == pAddr->sin_family)
                        {
                            inet_ntop(pAddr->sin_family, &pAddr->in6.sin6_addr, ipStr, sizeof(ipStr));
                        }

                        printf("result is %s\n", ipStr);
                    }

                    pRes = pRes->ai_next;
                }

                freeaddrinfo(pAddrInfo);
                pAddrInfo = NULL;
            }

            break;
        }

        case MODULE_STATE_ERROR:
        {
            break;
        }

        default:
        {
            break;
        }
    }
}
```

---
#### TCP Client

``` c
#include <string.h>

#include "winc_socket.h"

typedef enum
{
    MODULE_STATE_INIT,
    MODULE_STATE_SOCKET_WAITING,
    MODULE_STATE_CONNECTING,
    MODULE_STATE_CONNECTED,
    MODULE_STATE_DISCONNECTED,
    MODULE_STATE_ERROR,
} MODULE_STATE;

typedef struct
{
    union sockaddr_union sockAddr;
} BSOCK_TCP_CLIENT_INIT_TYPE;

static MODULE_STATE                 state;
static int                          sockh;
static BSOCK_TCP_CLIENT_INIT_TYPE   initData = {0};

void bsock_tcp_client_init(void *pInitData)
{
    if (NULL != pInitData)
    {
        memcpy(&initData, pInitData, sizeof(BSOCK_TCP_CLIENT_INIT_TYPE));
    }

    state = MODULE_STATE_INIT;
}

void bsock_tcp_client_run(void)
{
    switch (state)
    {
        case MODULE_STATE_INIT:
        {
            state = MODULE_STATE_ERROR;

            sockh = socket(initData.sockAddr.sin_family, SOCK_STREAM, IPPROTO_TCP);

            if (sockh < 0)
            {
                break;
            }

            printf("opening socket %d\n", sockh);

            /* Fall through */
        }

        case MODULE_STATE_SOCKET_WAITING:
        {
            errno = 0;
            if (-1 == connect(sockh, (struct sockaddr*)&initData.sockAddr, sizeof(initData.sockAddr)))
            {
                if (EINPROGRESS == errno)
                {
                    printf("connection in progress\n");
                    state = MODULE_STATE_CONNECTING;
                }
                else if (EAGAIN == errno)
                {
                    printf("socket not ready try again\n");
                    state = MODULE_STATE_SOCKET_WAITING;
                }
                else
                {
                    printf("connect failed, errno is %d\n", errno);
                    state = MODULE_STATE_ERROR;
                }
            }
            else
            {
                printf("socket connected\n");
                state = MODULE_STATE_CONNECTED;
            }

            break;
        }

        case MODULE_STATE_CONNECTING:
        {
            struct pollfd fd;

            fd.fd     = sockh;
            fd.events = POLLOUT;

            if (-1 == poll(&fd, 1, 0))
            {
                state = MODULE_STATE_ERROR;
                break;
            }

            if (0 != (fd.revents & POLLERR))
            {
                printf("connect failed\n");
                state = MODULE_STATE_ERROR;
            }

            if (0 != (fd.revents & POLLOUT))
            {
                printf("socket connected\n");
                state = MODULE_STATE_CONNECTED;
            }

            break;
        }

        case MODULE_STATE_CONNECTED:
        {
            struct pollfd fd;
            ssize_t numBytes = 0;
            uint8_t buffer[128];

            fd.fd     = sockh;
            fd.events = POLLIN|POLLOUT;

            if (-1 == poll(&fd, 1, 0))
            {
                state = MODULE_STATE_ERROR;
                break;
            }

            if (0 != (fd.revents & POLLIN))
            {
                errno = 0;
                numBytes = recv(sockh, NULL, 0, MSG_PEEK|MSG_TRUNC);

                if ((numBytes <= 0) && (errno != EWOULDBLOCK))
                {
                    state = MODULE_STATE_DISCONNECTED;
                    break;
                }

                if (numBytes >= sizeof(buffer))
                {
                    numBytes = sizeof(buffer);
                }

                errno = 0;
                numBytes = recv(sockh, buffer, numBytes, 0);
                if (numBytes <= 0)
                {
                    if (errno != EWOULDBLOCK)
                    {
                        printf("recv failed, errno is %d\n", errno);
                        state = MODULE_STATE_DISCONNECTED;
                        break;
                    }
                }

                printf("recv: %d\n", numBytes);
            }

            if (0 != (fd.revents & POLLHUP))
            {
                printf("socket disconnected\n");

                if (0 == (fd.revents & POLLIN))
                {
                    state = MODULE_STATE_DISCONNECTED;
                }
            }

            if (0 != (fd.revents & POLLOUT))
            {
                if (numBytes > 0)
                {
                    errno = 0;
                    numBytes = send(sockh, buffer, numBytes, 0);

                    if ((numBytes < 0) && (errno != EWOULDBLOCK) && (errno != EAGAIN))
                    {
                        printf("send failed, errno is %d\n", errno);
                        state = MODULE_STATE_DISCONNECTED;
                        break;
                    }
                }
            }

            break;
        }

        case MODULE_STATE_DISCONNECTED:
        {
            if (0 != sockh)
            {
                shutdown(sockh, SHUT_RDWR);
                sockh = 0;
            }
            break;
        }

        case MODULE_STATE_ERROR:
        {
            break;
        }

        default:
        {
            break;
        }
    }
}
```

---
#### TCP Server

``` c
#include <string.h>

#include "winc_socket.h"

#define TCP_SERVER_MAX_CLIENTS  2

typedef enum
{
    MODULE_STATE_INIT,
    MODULE_STATE_SOCKET_WAITING,
    MODULE_STATE_LISTEN,
    MODULE_STATE_LISTENING,
    MODULE_STATE_ERROR,
} MODULE_STATE;

typedef struct
{
    union sockaddr_union sockAddr;
} BSOCK_TCP_SERVER_INIT_TYPE;

static MODULE_STATE                 state;
static int                          sockh;
static int                          sockhClient[TCP_SERVER_MAX_CLIENTS] = {0};
static BSOCK_TCP_SERVER_INIT_TYPE   initData = {0};

void bsock_tcp_server_init(void *pInitData)
{
    if (NULL != pInitData)
    {
        memcpy(&initData, pInitData, sizeof(BSOCK_TCP_SERVER_INIT_TYPE));
    }

    state = MODULE_STATE_INIT;
}

void bsock_tcp_server_run(void)
{
    switch (state)
    {
        case MODULE_STATE_INIT:
        {
            state = MODULE_STATE_ERROR;

            sockh = socket(initData.sockAddr.sin_family, SOCK_STREAM, IPPROTO_TCP);

            if (sockh < 0)
            {
                break;
            }

            printf("opening socket %d\n", sockh);

            /* Fall through */
        }

        case MODULE_STATE_SOCKET_WAITING:
        {
            errno = 0;
            if (-1 == bind(sockh, (struct sockaddr*)&initData.sockAddr, sizeof(initData.sockAddr)))
            {
                printf("bind failed, errno is %d\n", errno);
                state = MODULE_STATE_ERROR;
                break;
            }

            printf("socket bound\n");

            /* Fall through */
        }

        case MODULE_STATE_LISTEN:
        {
            errno = 0;
            if (-1 == listen(sockh, TCP_SERVER_MAX_CLIENTS))
            {
                if (EAGAIN == errno)
                {
                    printf("socket not ready try again\n");
                    state = MODULE_STATE_LISTEN;
                }
                else
                {
                    printf("listen failed, errno is %d\n", errno);
                    state = MODULE_STATE_ERROR;
                }
            }
            else
            {
                printf("socket listening\n");
                state = MODULE_STATE_LISTENING;
            }

            break;
        }

        case MODULE_STATE_LISTENING:
        {
            int i;
            int numfds = 1;

            struct pollfd fd[1+TCP_SERVER_MAX_CLIENTS] = {0};

            fd[0].fd     = sockh;
            fd[0].events = POLLIN;

            for (i=0; i<TCP_SERVER_MAX_CLIENTS; i++)
            {
                fd[i+1].fd = sockhClient[i];

                if (0 != fd[i+1].fd)
                {
                    fd[i+1].events = POLLIN|POLLOUT;
                    numfds++;
                }
            }

            if (-1 == poll(fd, numfds, 0))
            {
                state = MODULE_STATE_ERROR;
                break;
            }

            if (0 != (fd[0].revents & POLLIN))
            {
                for (i=0; i<TCP_SERVER_MAX_CLIENTS; i++)
                {
                    union sockaddr_union sockAddr;
                    socklen_t sockAddrLen = sizeof(union sockaddr_union);
                    char ipStr[64];

                    if (0 == sockhClient[i])
                    {
                        sockhClient[i] = accept(sockh, (struct sockaddr*)&sockAddr, &sockAddrLen);

                        if (-1 == sockhClient[i])
                        {
                            sockhClient[i] = 0;
                        }
                        else
                        {
                            if (AF_INET == sockAddr.sin_family)
                            {
                                inet_ntop(sockAddr.sin_family, &sockAddr.in4.sin_addr, ipStr, sizeof(ipStr));
                            }
                            else if (AF_INET6 == sockAddr.sin_family)
                            {
                                inet_ntop(sockAddr.sin_family, &sockAddr.in6.sin6_addr, ipStr, sizeof(ipStr));
                            }

                            printf("accept %d from %s:%d\n", sockhClient[i], ipStr, ntohs(sockAddr.sin_port));
                        }

                        break;
                    }
                }
            }

            for (i=1; i<=TCP_SERVER_MAX_CLIENTS; i++)
            {
                if ((0 != fd[i].fd) && (0 != fd[i].revents))
                {
                    ssize_t numBytes = 0;
                    uint8_t buffer[128];

                    if (0 != (fd[i].revents & POLLIN))
                    {
                        errno = 0;
                        numBytes = recv(fd[i].fd, NULL, 0, MSG_PEEK|MSG_TRUNC);

                        if ((numBytes <= 0) && (errno != EWOULDBLOCK))
                        {
                            shutdown(fd[i].fd, SHUT_RDWR);
                            sockhClient[i-1] = 0;
                            break;
                        }

                        if (numBytes >= sizeof(buffer))
                        {
                            numBytes = sizeof(buffer);
                        }

                        errno = 0;
                        numBytes = recv(fd[i].fd, buffer, numBytes, 0);
                        if (numBytes <= 0)
                        {
                            if (errno != EWOULDBLOCK)
                            {
                                printf("recv failed, errno is %d\n", errno);
                                shutdown(fd[i].fd, SHUT_RDWR);
                                sockhClient[i-1] = 0;
                                break;
                            }
                        }

                        printf("recv: %d\n", numBytes);
                    }

                    if (0 != (fd[i].revents & POLLHUP))
                    {
                        printf("socket disconnected\n");

                        if (0 == (fd[i].revents & POLLIN))
                        {
                            shutdown(fd[i].fd, SHUT_RDWR);
                            sockhClient[i-1] = 0;
                            break;
                        }
                    }

                    if (0 != (fd[i].revents & POLLOUT))
                    {
                        if (numBytes > 0)
                        {
                            errno = 0;
                            numBytes = send(fd[i].fd, buffer, numBytes, 0);

                            if ((numBytes < 0) && (errno != EWOULDBLOCK) && (errno != EAGAIN))
                            {
                                printf("send failed, errno is %d\n", errno);
                                shutdown(fd[i].fd, SHUT_RDWR);
                                sockhClient[i-1] = 0;
                                break;
                            }
                        }
                    }
                }
            }

            break;
        }

        case MODULE_STATE_ERROR:
        {
            break;
        }

        default:
        {
            break;
        }
    }
}
```

---
#### UDP Client

``` c
#include <string.h>

#include "winc_socket.h"

typedef enum
{
    MODULE_STATE_INIT,
    MODULE_STATE_SOCKET_WAITING,
    MODULE_STATE_CONNECTING,
    MODULE_STATE_CONNECTED,
    MODULE_STATE_DISCONNECTED,
    MODULE_STATE_ERROR,
} MODULE_STATE;

typedef struct
{
    union sockaddr_union sockAddr;
} BSOCK_UDP_CLIENT_INIT_TYPE;

static MODULE_STATE                 state;
static int                          sockh;
static BSOCK_UDP_CLIENT_INIT_TYPE   initData = {0};

void bsock_udp_client_init(void *pInitData)
{
    if (NULL != pInitData)
    {
        memcpy(&initData, pInitData, sizeof(BSOCK_UDP_CLIENT_INIT_TYPE));
    }

    state = MODULE_STATE_INIT;
}

void bsock_udp_client_run(void)
{
    switch (state)
    {
        case MODULE_STATE_INIT:
        {
            state = MODULE_STATE_ERROR;

            sockh = socket(initData.sockAddr.sin_family, SOCK_DGRAM, IPPROTO_UDP);

            if (sockh < 0)
            {
                break;
            }

            printf("opening socket %d\n", sockh);

            /* Fall through */
        }

        case MODULE_STATE_SOCKET_WAITING:
        {
            errno = 0;
            if (-1 == connect(sockh, (struct sockaddr*)&initData.sockAddr, sizeof(initData.sockAddr)))
            {
                if (EINPROGRESS == errno)
                {
                    printf("connection in progress\n");
                    state = MODULE_STATE_CONNECTING;
                }
                else if (EAGAIN == errno)
                {
                    printf("socket not ready try again\n");
                    state = MODULE_STATE_SOCKET_WAITING;
                }
                else
                {
                    printf("connect failed, errno is %d\n", errno);
                    state = MODULE_STATE_ERROR;
                }
            }
            else
            {
                printf("socket connected\n");
                state = MODULE_STATE_CONNECTED;
            }

            break;
        }

        case MODULE_STATE_CONNECTING:
        {
            struct pollfd fd;

            fd.fd     = sockh;
            fd.events = POLLOUT;

            if (-1 == poll(&fd, 1, 0))
            {
                state = MODULE_STATE_ERROR;
                break;
            }

            if (0 != (fd.revents & POLLERR))
            {
                printf("connect failed\n");
                state = MODULE_STATE_ERROR;
            }

            if (0 != (fd.revents & POLLOUT))
            {
                printf("socket connected\n");
                state = MODULE_STATE_CONNECTED;

                send(sockh, "Hello\n", 6, 0);
            }

            break;
        }

        case MODULE_STATE_CONNECTED:
        {
            struct pollfd fd;
            ssize_t numBytes = 0;
            uint8_t buffer[128];

            fd.fd     = sockh;
            fd.events = POLLIN|POLLOUT;

            if (-1 == poll(&fd, 1, 0))
            {
                state = MODULE_STATE_ERROR;
                break;
            }

            if (0 != (fd.revents & POLLIN))
            {
                union sockaddr_union sockAddr;
                socklen_t fromLen = sizeof(sockAddr);
                char ipStr[64];

                errno = 0;
                numBytes = recvfrom(sockh, NULL, 0, MSG_PEEK|MSG_TRUNC, NULL, NULL);

                if ((numBytes <= 0) && (errno != EWOULDBLOCK))
                {
                    state = MODULE_STATE_DISCONNECTED;
                    break;
                }

                if (numBytes >= sizeof(buffer))
                {
                    numBytes = sizeof(buffer);
                }

                errno = 0;
                numBytes = recvfrom(sockh, buffer, numBytes, 0, (struct sockaddr*)&sockAddr, &fromLen);
                if (numBytes <= 0)
                {
                    if (errno != EWOULDBLOCK)
                    {
                        printf("recv failed, errno is %d\n", errno);
                        state = MODULE_STATE_DISCONNECTED;
                        break;
                    }
                }

                if (AF_INET == sockAddr.sin_family)
                {
                    inet_ntop(sockAddr.sin_family, &sockAddr.in4.sin_addr, ipStr, sizeof(ipStr));
                }
                else if (AF_INET6 == sockAddr.sin_family)
                {
                    inet_ntop(sockAddr.sin_family, &sockAddr.in6.sin6_addr, ipStr, sizeof(ipStr));
                }

                printf("recv: %d from %s:%d\n", numBytes, ipStr, ntohs(sockAddr.sin_port));
            }

            if (0 != (fd.revents & POLLOUT))
            {
                if (numBytes > 0)
                {
                    errno = 0;
                    numBytes = send(sockh, buffer, numBytes, 0);

                    if ((numBytes < 0) && (errno != EWOULDBLOCK) && (errno != EAGAIN))
                    {
                        printf("send failed, errno is %d\n", errno);
                        state = MODULE_STATE_DISCONNECTED;
                        break;
                    }
                }
            }

            break;
        }

        case MODULE_STATE_DISCONNECTED:
        {
            if (0 != sockh)
            {
                shutdown(sockh, SHUT_RDWR);
                sockh = 0;
            }
            break;
        }

        case MODULE_STATE_ERROR:
        {
            break;
        }

        default:
        {
            break;
        }
    }
}
```

---
#### UDP Server

``` c
#include <string.h>

#define UDP_SERVER_MAX_CLIENTS  2

typedef enum
{
    MODULE_STATE_INIT,
    MODULE_STATE_SOCKET_WAITING,
    MODULE_STATE_LISTENING,
    MODULE_STATE_DISCONNECTED,
    MODULE_STATE_ERROR,
} MODULE_STATE;

typedef struct
{
    union sockaddr_union sockAddr;
} BSOCK_UDP_SERVER_INIT_TYPE;

static MODULE_STATE                 state;
static int                          sockh;
static BSOCK_UDP_SERVER_INIT_TYPE   initData = {0};

void bsock_udp_server_init(void *pInitData)
{
    if (NULL != pInitData)
    {
        memcpy(&initData, pInitData, sizeof(BSOCK_UDP_SERVER_INIT_TYPE));
    }

    state = MODULE_STATE_INIT;
}

void bsock_udp_server_run(void)
{
    switch (state)
    {
        case MODULE_STATE_INIT:
        {
            state = MODULE_STATE_ERROR;

            sockh = socket(initData.sockAddr.sin_family, SOCK_DGRAM, IPPROTO_UDP);

            if (sockh < 0)
            {
                break;
            }

            printf("opening socket %d\n", sockh);

            /* Fall through */
        }

        case MODULE_STATE_SOCKET_WAITING:
        {
            errno = 0;
            if (-1 == bind(sockh, (struct sockaddr*)&initData.sockAddr, sizeof(initData.sockAddr)))
            {
                if (EAGAIN == errno)
                {
                    printf("socket not ready try again\n");
                    state = MODULE_STATE_SOCKET_WAITING;
                }
                else
                {
                    printf("bind failed, errno is %d\n", errno);
                    state = MODULE_STATE_ERROR;
                }
            }
            else
            {
                printf("socket bound\n");
                state = MODULE_STATE_LISTENING;
            }

            break;
        }

        case MODULE_STATE_LISTENING:
        {
            struct pollfd fd;
            ssize_t numBytes = 0;
            uint8_t buffer[128];
            union sockaddr_union sockAddr;

            fd.fd     = sockh;
            fd.events = POLLIN|POLLOUT;

            if (-1 == poll(&fd, 1, 0))
            {
                state = MODULE_STATE_ERROR;
                break;
            }

            if (0 != (fd.revents & POLLIN))
            {
                socklen_t fromLen = sizeof(sockAddr);
                char ipStr[64];

                errno = 0;
                numBytes = recvfrom(sockh, NULL, 0, MSG_PEEK|MSG_TRUNC, NULL, NULL);

                if ((numBytes <= 0) && (errno != EWOULDBLOCK))
                {
                    state = MODULE_STATE_DISCONNECTED;
                    break;
                }

                if (numBytes >= sizeof(buffer))
                {
                    numBytes = sizeof(buffer);
                }

                errno = 0;
                numBytes = recvfrom(sockh, buffer, numBytes, 0, (struct sockaddr*)&sockAddr, &fromLen);
                if (numBytes <= 0)
                {
                    if (errno != EWOULDBLOCK)
                    {
                        printf("recv failed, errno is %d\n", errno);
                        state = MODULE_STATE_DISCONNECTED;
                        break;
                    }
                }

                if (AF_INET == sockAddr.sin_family)
                {
                    inet_ntop(sockAddr.sin_family, &sockAddr.in4.sin_addr, ipStr, sizeof(ipStr));
                }
                else if (AF_INET6 == sockAddr.sin_family)
                {
                    inet_ntop(sockAddr.sin_family, &sockAddr.in6.sin6_addr, ipStr, sizeof(ipStr));
                }

                printf("recv: %d from %s:%d\n", numBytes, ipStr, ntohs(sockAddr.sin_port));
            }

            if (0 != (fd.revents & POLLOUT))
            {
                if (numBytes > 0)
                {
                    errno = 0;
                    numBytes = sendto(sockh, buffer, numBytes, 0, (struct sockaddr*)&sockAddr, sizeof(sockAddr));

                    if ((numBytes < 0) && (errno != EWOULDBLOCK) && (errno != EAGAIN))
                    {
                        printf("send failed, errno is %d\n", errno);
                        state = MODULE_STATE_DISCONNECTED;
                        break;
                    }
                }
            }

            break;
        }

        case MODULE_STATE_DISCONNECTED:
        {
            if (0 != sockh)
            {
                shutdown(sockh, SHUT_RDWR);
                sockh = 0;
            }
            break;
        }

        case MODULE_STATE_ERROR:
        {
            break;
        }

        default:
        {
            break;
        }
    }
}
```

---
---
## List of Examples

<table>
<tbody>
<tr>
<td>Module</td>
<td>Description</td>
</tr>
<tr>
<td>Configuration Functions</td>
<td><a href="#EXAMPLE_ReadAllParamVal">Reading all parameter values</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_ReadSingleVal">To read a single value</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SetAddVal">To set an additional value</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_ReplaceAddVal">To replace an existing value</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_ValIDRange">Range of IDs</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SimpleIDVal">Simple ID/Value</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_ComplexIDVal">Complex ID/Value</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_Preset0IDVal">Using preset 0</a></td>
</tr>
<tr>
<td>CFG</td>
<td><a href="#EXAMPLE_dc6130cfe9a84137759d254f2f775e9c95a1a939">Saving active configuration to storage</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_52043c5b1266965e87fee1d62cf0473db94a8a9f">Restoring configuration from storage</a></td>
</tr>
<tr>
<td>DNS</td>
<td><a href="#EXAMPLE_1a51414e8ba4741b94b30368131eea0cbb47bc44">A record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_16834ed81435ec93ee5ab05838d2049cfc926893">NS record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_cee6b3bece566292845ee70ea593b9ac8aba61e9">CNAME record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_0e97d9dea705e94b6d7a47e08f327b1dbda26c32">SOA record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_63f20427cb830943792a52dd0a405d79e485df24">PTR record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_cbb40c171c40e12c1958a6d28ccc5ce92c11459e">MX record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_5cf4dd868566a7d4fdc78b7c53ddcfa7a037d936">TXT record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_c4b68ffc231410a6beda9e466887b74c3303c800">AAAA record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_28e1b5f3b9c1a408085681aa145de2efbbd6e948">SRV record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_d2156535c655505f729023b004f3d04d06179bf0">DS record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_ea72626e881fc800924086c49107f7286274d8d5">NSEC record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_28a3cea6a630e35c1ab57bdc97cffb510aa9b719">DNSKEY record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_4bb82ae1e9ae5473ddf7c13902fcf71c771395d2">ANY record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_0f54ad37f94345566cd88df9220d1c69b75d32c3">A record query With DNSSEC awareness</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_e84478c18562abdd4e2bbc34a253cfb7f08e4f8c">NSEC3PARAM (unknown type) record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_214c64db604a29b4ab723f35f946650640cabcd6">NSEC3 (unknown type) response to invalid A record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_de863d68160befb7fb06d0eb444512ffff122839">Multicast A record query</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_47cd0626aaaf78a7d83763f709beb232b7a5a058">MDNS-SD of local SSH services</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_9877579559e5e434da23523503bbceaaebdd6a80">List and delete a file</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_2e74f1ef2b6c2ef83ee4e90cb9de68a8a92de661">Get filesystem information</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_0d368b631cc611ff30c1bc5a3025bc5aee1f7d59">File load using FS-TSFR protocol</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_a1c1b6e4bee3b5a03437950d9aaa8e7e4cced18f">File store using FS-TSFR protocol</a></td>
</tr>
<tr>
<td>MQTT</td>
<td><a href="#EXAMPLE_763df688af86d232581b5749c292a4aadffbdcd4">MQTT connection directly over TLS</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_8cb9b789fe72ee96a4f00e56c7528fefed94d312">MQTT connection over TLS socket</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_520a41f5f278cbdca5ec88603f0abace550e4c65">Subscribe to MQTT topic and receive data (asynchronously)</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_e86e402f305e460d8856aba5d60360834676ed35">Subscribe to MQTT topic and receive data (polled)</a></td>
</tr>
<tr>
<td>OTA</td>
<td><a href="#EXAMPLE_OTA_HTTP_CONF">Internal OTA HTTP Configuration</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_OTA_HTTPS_CONF">Internal OTA HTTPS Configuration</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_OTA_INTERNAL">Internal OTA</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_OTA_NVM">NVM OTA</a></td>
</tr>
<tr>
<td>SOCKET</td>
<td><a href="#EXAMPLE_SOCKO_1">Opening a TCP server socket</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SOCKRD_1">Basic socket read</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SOCKRD_2">In-band socket read</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SOCKRXT_1">Simple asynchronous socket read</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SOCKRXT_2">Reliable asynchronous socket read</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SOCKTLSCLI">Set TLS configuration 1 for TLS client</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_12de0326b22680d3b9cc3d612dba34e5f4d023fe">Open a TLS client socket with AT+SOCK</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SOCKTLSSRV">Set TLS configuration 2 for TLS server</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_a70e12e9f2deb08dda4c674bca8584fd9c59e257">Open a TLS server socket with AT+SOCK</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_SOCKRDBUF">Reading partial datagram</a></td>
</tr>
<tr>
<td>TLS</td>
<td><a href="#EXAMPLE_TLS_DIGEST">Peer certificate digest pinning with WINC_CmdTLSCDA</a></td>
</tr>
<tr>
<td>WSCN</td>
<td><a href="#EXAMPLE_WSCN_SECURITY">Scan for Access Points and filter by security type</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_286d6c7f74c01a7bacc3d6fcaa240ad067b1f736">Setting SSID filter with WINC_CmdWSCNC</a></td>
</tr>
<tr>
<td>WSTA</td>
<td><a href="#EXAMPLE_WSTA_PERSONAL">WPA Personal: Configure STA connection parameters</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_WSTA_CONNECT">Connect at Wi-Fi and IP layers</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_WSTA_RECONNECT">Some disconnections, reconnections and roaming</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_WSTA_ENTERPRISE_TUNNEL">WPA Enterprise: Configure a TLS context for establishing a tunnel</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_WSTA_ENTERPRISE_MSCHAPV2">WPA Enterprise: Configure STA connection parameters for MSCHAPv2</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_WSTA_ENTERPRISE_TLS_TLSC">WPA Enterprise: Configure a TLS context for EAP-PEAPv1/TLS</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_WSTA_ENTERPRISE_TLS_WSTAC">WPA Enterprise: Configure STA connection parameters for EAP-PEAPv1/TLS</a></td>
</tr>
<tr>
<td>DI</td>
<td><a href="#EXAMPLE_b24cb7601966bd304010fa7449e5f57c0507b958">Query device information with WINC_CmdDI</a></td>
</tr>
<tr>
<td>EXTCRYPTO</td>
<td><a href="#EXAMPLE_EXTCRYPTO_TLS">Example of TLS configuration for secure signing via external crypto operations</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_EXTCRYPTO">Example of signing request/response using WINC_CmdEXTCRYPTO</a></td>
</tr>
<tr>
<td>WIFI</td>
<td><a href="#EXAMPLE_83aadd2a5891271329d9dc62f4cea81d34571a9e">Settings with WINC_CmdWIFIC</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_c37bae967b299185b054858a003c7507e0b388a9">WINC_CmdWIFIC coexistence settings for 3-wire PTA interface</a></td>
</tr>
<tr>
<td>NVM</td>
<td><a href="#EXAMPLE_NVM_EXAMPLE">Simple example of NVM usage</a></td>
</tr>
<tr>
<td>DFU</td>
<td><a href="#EXAMPLE_154f5dd58fe255da7480e1634642e778c98de910">Example of using WINC_CmdDFUADR and WINC_CmdDFUSEQ</a></td>
</tr>
<tr>
<td>PPS</td>
<td><a href="#EXAMPLE_PPS_1">Configuring and enabling PPS</a></td>
</tr>
<tr>
<td>ARB</td>
<td><a href="#EXAMPLE_43ad9746b269d7ef860794a7d75c34ef47c94f97">Example of using WINC_CmdARB</a></td>
</tr>
<tr>
<td>HTTP</td>
<td><a href="#EXAMPLE_HTTP_1">HTTPS download</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_HTTP_2">HTTPS download from TCP socket</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_HTTP_3">File download to local filesystem</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_HTTP_4">HTTPGET with path and query/fragments</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_HTTP_5">HTTP basic authentication using additional request headers</a></td>
</tr>
</tbody>
</table>

---