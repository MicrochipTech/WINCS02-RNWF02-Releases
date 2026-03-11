/*
 * WINCS02 nc_driver — Platform Porting Template
 *
 * This file provides stub implementations of the platform-specific functions
 * required by the WINCS02 nc_driver. Replace the TODO sections with code
 * for your target MCU and SPI peripheral.
 *
 * Steps to port:
 *   1. Copy this file into your project and rename it (e.g. winc_port_myplatform.c)
 *   2. Copy port/conf_winc_dev.h to your project include path — adjust settings
 *   3. Implement the functions below for your hardware
 *   4. See the Binary Protocol API Specification (PDF) for protocol details
 *
 * The complete initialisation and event-loop example at the bottom of this
 * file shows the full sequence needed to get the WINCS02 running.
 */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "winc_dev.h"
#include "winc_sdio_drv.h"
#include "winc_cmds.h"
#include "winc_cmd_req.h"

/*============================================================================
 * PLATFORM FUNCTIONS — implement these for your MCU
 *==========================================================================*/

/*----------------------------------------------------------------------------
 * SPI Send/Receive  (REQUIRED)
 *
 * This is the core platform function. The nc_driver calls it via a function
 * pointer of type WINC_SDIO_SEND_RECEIVE_FP (defined in winc_sdio_drv.h):
 *
 *   typedef bool (*WINC_SDIO_SEND_RECEIVE_FP)(
 *       void* pTransmitData,
 *       void* pReceiveData,
 *       size_t size
 *   );
 *
 * Requirements:
 *   - SPI Mode 0 (CPOL=0, CPHA=0), MSB first
 *   - Maximum SPI clock: 50 MHz (refer to WINCS02 datasheet Table 3-11;
 *     actual max may be lower depending on PCB layout)
 *   - CS must be ASSERTED (driven low) at the START of each call
 *   - CS must be DEASSERTED (driven high) at the END of each call
 *   - When pTransmitData is NULL, transmit 0xFF for each byte
 *     (the WINCS02 interprets 0x00 on MOSI as valid data)
 *   - When pReceiveData is NULL, discard received bytes
 *   - Return true on success, false on failure
 *
 * This function is passed to WINC_SDIODeviceInit() during initialisation.
 *--------------------------------------------------------------------------*/
bool WINC_PORT_SPISendReceive(void *pTransmitData, void *pReceiveData, size_t size)
{
    uint8_t *pTx = (uint8_t *)pTransmitData;
    uint8_t *pRx = (uint8_t *)pReceiveData;

    /* TODO: Replace with your MCU's SPI and GPIO calls.
     *
     * Example for a byte-at-a-time SPI peripheral:
     *
     *   GPIO_PinClear(SPI_CS_PIN);                       // Assert CS
     *
     *   for (size_t i = 0; i < size; i++) {
     *       uint8_t txByte = (pTx != NULL) ? pTx[i] : 0xFFU;
     *       uint8_t rxByte = SPI_Transfer(txByte);        // Full-duplex byte
     *       if (pRx != NULL) {
     *           pRx[i] = rxByte;
     *       }
     *   }
     *
     *   GPIO_PinSet(SPI_CS_PIN);                          // Deassert CS
     *   return true;
     */

    (void)pTx;
    (void)pRx;
    (void)size;
    return false;
}

/*----------------------------------------------------------------------------
 * MCLR Reset Pin Control  (REQUIRED)
 *
 * The MCLR pin is active-low. Driving it low puts the WINCS02 into reset.
 * Releasing it high allows the module to boot.
 *--------------------------------------------------------------------------*/

static void WINC_PORT_ResetAssert(void)
{
    /* TODO: Drive MCLR pin LOW (assert reset) */
}

static void WINC_PORT_ResetDeassert(void)
{
    /* TODO: Drive MCLR pin HIGH (release reset) */
}

/*----------------------------------------------------------------------------
 * INTOUT Pin Read  (REQUIRED)
 *
 * The WINCS02 INTOUT pin (active-low, push-pull) signals when the module
 * has data for the host to read. Check this pin in your main loop.
 *--------------------------------------------------------------------------*/

static bool WINC_PORT_IsInterruptAsserted(void)
{
    /* TODO: Return true if INTOUT pin is LOW (interrupt asserted)
     *
     *   return (GPIO_PinRead(INTOUT_PIN) == 0);
     */
    return false;
}

/*----------------------------------------------------------------------------
 * Delay  (REQUIRED)
 *
 * Blocking millisecond delay used during initialisation.
 *--------------------------------------------------------------------------*/

static void WINC_PORT_DelayMs(uint32_t ms)
{
    /* TODO: Implement blocking delay for your platform.
     *
     * SysTick, a hardware timer, or a simple busy-wait loop all work.
     */
    (void)ms;
}

/*----------------------------------------------------------------------------
 * Debug Printf  (OPTIONAL but highly recommended)
 *
 * Route driver debug output to your serial console (UART, SWO, etc.).
 * Call WINC_DevSetDebugPrintf() with this function during init.
 * Set WINC_DEBUG_LEVEL in conf_winc_dev.h to control verbosity.
 *--------------------------------------------------------------------------*/

/*
static void WINC_PORT_DebugPrintf(const char *format, ...)
{
    // TODO: Implement printf-style output to your debug console
}
*/

/*============================================================================
 * COMPLETE INITIALISATION AND EVENT-LOOP EXAMPLE
 *
 * Uncomment and adapt for your application.
 *==========================================================================*/

/*

// Receive buffer — must persist for the lifetime of the driver.
// 4096 bytes is sufficient for basic operation (scan, connect, sockets).
static uint8_t s_receiveBuffer[4096];

// Event interrupt check callback — passed to WINC_DevHandleEvent().
// Must return true while the INTOUT pin is still asserted (low).
static bool eventIntCheck(void)
{
    return WINC_PORT_IsInterruptAsserted();
}

// AEC (Asynchronous Event Callback) — receives unsolicited events from
// the WINCS02 such as scan results, link up/down, IP assignment, etc.
static void aecCallback(uintptr_t context, WINC_DEVICE_HANDLE devHandle,
                         const WINC_DEV_EVENT_RSP_ELEMS *const pElems)
{
    (void)context;
    (void)devHandle;

    if (NULL == pElems) return;

    switch (pElems->rspId) {

        case WINC_AEC_ID_WSCNIND:
            // WiFi scan result (one per AP found)
            // Elements: [0]=RSSI(int8), [1]=SecType(uint8), [2]=Channel(uint8),
            //           [3]=BSSID(mac), [4]=SSID(string)
            break;

        case WINC_AEC_ID_WSCNDONE:
            // WiFi scan complete
            break;

        case WINC_AEC_ID_WSTALU:
            // WiFi station link up
            // Elements: [0]=AssocID(uint16), [1]=BSSID(mac), [2]=Channel(uint8)
            break;

        case WINC_AEC_ID_WSTALD:
            // WiFi station link down
            break;

        case WINC_AEC_ID_WSTAAIP:
            // WiFi station IP address assigned
            break;

        default:
            break;
    }
}

// Command response callback — handles the lifecycle of command requests.
// The buffer allocated for the command request is freed here on completion.
static void cmdRspCallback(uintptr_t context, WINC_DEVICE_HANDLE devHandle,
                            WINC_CMD_REQ_HANDLE cmdReqHandle,
                            WINC_DEV_CMDREQ_EVENT_TYPE event,
                            uintptr_t eventArg)
{
    (void)context;
    (void)devHandle;
    (void)eventArg;

    if (WINC_DEV_CMDREQ_EVENT_STATUS_COMPLETE == event) {
        // End of command lifecycle — free the buffer that was malloc'd
        free((void *)cmdReqHandle);
    }
}

// Helper — allocate and initialise a command request buffer.
// Returns WINC_CMD_REQ_INVALID_HANDLE on failure.
static WINC_CMD_REQ_HANDLE allocCmdReq(unsigned int numCommands,
                                        size_t extraDataLen,
                                        WINC_DEV_CMD_RSP_CB pfCallback,
                                        uintptr_t ctx)
{
    size_t bufSz = (128U * numCommands) + extraDataLen;
    void *pBuf = malloc(bufSz);
    if (NULL == pBuf) return WINC_CMD_REQ_INVALID_HANDLE;

    WINC_CMD_REQ_HANDLE h = WINC_CmdReqInit(pBuf, bufSz, (int)numCommands,
                                              pfCallback, ctx);
    if (WINC_CMD_REQ_INVALID_HANDLE == h) free(pBuf);
    return h;
}

// ---- Main application entry point ----

int main(void)
{
    WINC_DEVICE_HANDLE devHandle;
    WINC_SDIO_STATE_TYPE sdioState;
    WINC_SDIO_STATUS_TYPE sdioStatus;
    WINC_DEV_INIT devInit;

    // --- Platform init (clocks, GPIO, SPI, UART) ---
    // TODO: Initialise your MCU peripherals here.

    // --- Optional: enable driver debug output ---
    // WINC_DevSetDebugPrintf(WINC_PORT_DebugPrintf);

    // --- Step 1: MCLR reset ---
    //
    // The WINCS02 requires a hardware reset before SDIO communication.
    // After releasing MCLR, the module takes approximately 3.5 seconds
    // to boot. During this time MISO reads 0x00 and SDIO init will
    // return WINC_SDIO_STATUS_RESET_WAITING.

    WINC_PORT_ResetAssert();
    WINC_PORT_DelayMs(100);         // Hold reset for 100ms
    WINC_PORT_ResetDeassert();

    // --- Step 2: Initialise the nc_driver device context ---

    devInit.pReceiveBuffer    = s_receiveBuffer;
    devInit.receiveBufferSize = sizeof(s_receiveBuffer);

    devHandle = WINC_DevInit(&devInit);
    if (WINC_DEVICE_INVALID_HANDLE == devHandle) {
        // Fatal: driver init failed
        while (1) ;
    }

    // --- Step 3: Initialise SDIO-over-SPI transport ---
    //
    // This handshakes with the WINCS02 over SPI using the SDIO protocol.
    // It must be retried with delays because the module needs time to boot.
    //
    // SDIO status codes (signed enum):
    //   OK (0)             — init complete, proceed
    //   RESET_WAITING (1)  — CMD0 waiting, module still booting, retry
    //   OP_WAITING (2)     — CMD5 waiting, retry
    //   OP_FAILED (-4)     — CMD5 failed, reset sdioState and retry
    //   RESET_FAILED (-5)  — CMD0 invalid response, check wiring
    //   ERROR (-2)         — unrecoverable

    sdioState = WINC_SDIO_STATE_UNKNOWN;

    for (int attempt = 0; attempt < 100; attempt++) {
        sdioStatus = WINC_SDIODeviceInit(&sdioState, WINC_PORT_SPISendReceive);

        if (WINC_SDIO_STATUS_OK == sdioStatus) {
            break;
        }

        if (WINC_SDIO_STATUS_RESET_WAITING == sdioStatus ||
            WINC_SDIO_STATUS_OP_WAITING == sdioStatus) {
            WINC_PORT_DelayMs(100);     // Wait for module to boot
            continue;
        }

        if (WINC_SDIO_STATUS_OP_FAILED == sdioStatus) {
            sdioState = WINC_SDIO_STATE_UNKNOWN;    // Reset and retry
            WINC_PORT_DelayMs(100);
            continue;
        }

        // Unrecoverable error — check SPI wiring and power
        while (1) ;
    }

    if (WINC_SDIO_STATUS_OK != sdioStatus) {
        // Timed out — module did not respond within ~10 seconds
        while (1) ;
    }

    // --- Step 4: Activate the bus ---
    //
    // The bus must be set to ACTIVE before sending any commands.

    WINC_DevBusStateSet(devHandle, WINC_DEV_BUS_STATE_ACTIVE);

    // --- Step 5: Register AEC callback ---
    //
    // This callback receives all unsolicited events (scan results,
    // link state changes, IP assignments, etc.).

    WINC_DevAECCallbackRegister(devHandle, aecCallback, 0);

    // --- Step 6: Send a command (WiFi scan example) ---

    {
        WINC_CMD_REQ_HANDLE cmdReqHandle;
        cmdReqHandle = allocCmdReq(1, 0, cmdRspCallback, 0);
        if (WINC_CMD_REQ_INVALID_HANDLE != cmdReqHandle) {
            WINC_CmdWSCN(cmdReqHandle, WINC_CONST_WSCN_ACT_PASV_ACTIVE);
            WINC_DevTransmitCmdReq(devHandle, cmdReqHandle);
        }
    }

    // --- Step 7: Main event loop ---
    //
    // The WINCS02 signals pending data via the INTOUT pin (active-low).
    // Poll it and call WINC_DevHandleEvent() when asserted.
    // WINC_DevUpdateEvent() processes received data and dispatches
    // callbacks (AEC events, command responses).

    while (1) {
        if (WINC_PORT_IsInterruptAsserted()) {
            WINC_DevHandleEvent(devHandle, eventIntCheck);
        }

        WINC_DevUpdateEvent(devHandle);
    }

    return 0;
}

*/
