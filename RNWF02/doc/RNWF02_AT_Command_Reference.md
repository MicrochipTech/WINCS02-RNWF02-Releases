# AT Command Specification

---
## Introduction

This reference manual provides information on the commands and features for Microchip products that utilize the Wi-Fi radio module command set. The Wi-Fi radio module is a complete, stand-alone embedded wireless LAN access device. The device has an on-board TCP/IP and TLS stack, and in the simplest hardware configuration, requires only four pins: Power, TX, RX, and Ground. Once the initial configuration has been performed, the device may access a Wi-Fi network and send/receive serial data.

### Product Support

**This reference manual refers to the Wi-Fi radio device:**

<table>
<tbody>
<tr>
<td>Name</td>
<td>Version</td>
<td>Revision</td>
</tr>
<tr>
<td>RNWF02</td>
<td>3.2.0</td>
<td>a1ac4a492</td>
</tr>
</tbody>
</table>

### Definitions

In this document, the following naming conventions are used:

- DCE (Data Communications Equipment): the Wi-Fi module.

- DTE (Data Terminal Equipment): the terminal that issues commands to the Wi-Fi module.

The DCE interfaces operates in one of two modes:

- Terminal mode: the DCE waits for AT commands and interprets all received characters as commands to execute. All commands must be terminated with a literal \<CR\>\<LF\> and these characters must not appear anywhere else in the command/parameter input stream. Parameters may be exchanged in one of two forms to accommodate binary data or infrequently-used ASCII control characters.

- Raw mode: the DTE transfers and accepts data "as is", i.e. in binary format with no post- or preprocessing.

### Asynchronous Event Codes

In most cases any output from the DCE will be in response to the receipt of a command from the DTE. There are cases, however, where an asynchronous event occurs that the DTE will need informing of (e.g. disconnection from the network). The DCE uses Asynchronous Event Codes (AEC) to convey such events; AECs use the same format conventions as regular responses with an initial \<CR\> to clearly identify the start of the AEC:

    <CR>+AECNAME:INFO<CR><LF>

To avoid confusion at the DTE, AECs will not be sent during the execution of a command. However the DTE must be prepared to receive AECs at any time as it is possible for the DCE to send ACEs resulting from a previous command or condition while the DTE is transmitting a new command.

### Commands and Responses

Command execution starts when the command line has been completed (\<CR\>\<LF\>) and ends when the result code for the command is sent consisting of either a success or error response.

The formatting of these responses depends on the current verbosity level set by the ATV command. All responses consist of the format \<RESPONSE\>\<CR\>\<LF\>.

<table>
<colgroup>
<col style="width: 20%" />
<col style="width: 40%" />
<col style="width: 40%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Level</th>
<th style="text-align: left;">Success Response Format</th>
<th style="text-align: left;">Error Response Format</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>1</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>1:&lt;STATUS_CODE&gt;</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>OK</p></td>
<td style="text-align: left;"><p>ERROR</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>OK</p></td>
<td style="text-align: left;"><p>ERROR:&lt;STATUS_CODE&gt;</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>OK</p></td>
<td style="text-align: left;"><p>ERROR:&lt;STATUS_MSG&gt;<br />
ERROR:&lt;STATUS_CODE&gt; (if no message defined)</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>OK</p></td>
<td style="text-align: left;"><p>ERROR:&lt;STATUS_CODE&gt;[,&lt;STATUS_MSG&gt;]</p></td>
</tr>
</tbody>
</table>

| Field           | Type    | Description                                    |
|-----------------|---------|------------------------------------------------|
| \<STATUS_CODE\> | Integer | Numeric status code, see Status Response Codes |
| \<STATUS_MSG\>  | String  | Descriptive text detailing the error           |

If a command requires longer to process the request, then the success response will be used to indicate that the command was accepted. Command processing continues asynchronously, further responses are indicated via AECs.

If an error occurs during asynchronous processing of a command the response will either be a command specific AEC or a generic error AEC of the format:

    <CR>+CMDNAME:ERRORRSP<CR><LF>

Where CNDNAME is the name of the command issued and encountering the error and ERRORRSP is an error response formatted as detailed in the table above. For example:

    <CR>+SOCKBR:ERROR:4<CR><LF>

### Numeric Mode

To simplify command/response interactions with automated systems where it may be more problematic to generate and parse string content, the DCE supports a numeric mode. In this mode commands and responses can be represented in number strings of fixed format.

Each command, response and AEC has a two part ID: a module ID and a command/AEC ID. These two numbers are combined in the form:

    MM:NN

Where MM is the hexadecimal representation of the module ID and NN is the hexadecimal representation of the command/AEC ID.

Commands can thus be issued as:

    AT+MM.NN=

Responses and AECs will be formatted as:

    +MM.NN:

While in numeric mode the DCE will still accept full command name strings as well as numeric format, but all responses and AECs will be in just numeric mode.

Numeric mode does not apply to the success or error responses returned by the DCE. If the DTE also wishes to use simplified formatting for these responses the command ATV can be used with either a parameter of 0 or 1 to replace 'OK' and 'ERROR' with '0' and '1'

---
## Overview

### Parameter Types

The definition of each command specifies the data types used for any associated parameters. The data types are as follows:

- Integer

- String

- Binary - used only in commands for sending data and receiving data where the DTE either specifies a length or puts the DCE into raw mode.

#### Integers

**Integers are used for numeric parameter values and may be specified in:**

<table>
<tbody>
<tr>
<td>base 2 (binary)</td>
<td>Format is '0b' followed by either characters '0' or '1'</td>
</tr>
<tr>
<td>base 8 (octal)</td>
<td>Format is '0o' followed by characters '0' through '7'</td>
</tr>
<tr>
<td>base 10 (decimal)</td>
<td>Format is an optional '-' character followed by characters '0' through '9'</td>
</tr>
<tr>
<td>base 16 (hexadecimal)</td>
<td>Format is '0x' followed by characters '0' through '9' and 'A' through 'F' (case insensitive)</td>
</tr>
</tbody>
</table>

**Examples:**

<table>
<tbody>
<tr>
<td>99</td>
<td>A value of ninety-nine.</td>
</tr>
<tr>
<td>-128</td>
<td>A value of negative one hundred and twenty-eight.</td>
</tr>
<tr>
<td>0b10110011</td>
<td>A value of 179.</td>
</tr>
<tr>
<td>0o6712</td>
<td>A value of 3530.</td>
</tr>
<tr>
<td>0xABCD</td>
<td>A value of 43981.</td>
</tr>
</tbody>
</table>

Positive integers are limited to 0 to 4,294,967,295 (i.e. 32 bits) Negative integers are limited to -1 to -2,147,483,648.

#### Fractional Integers:

Some parameters and responses support fractional integers, these are base 10 (decimal) only. They are composed of two integers with a period '.' separator, the second integer must be positive.

Examples:

- 1.1

- 5.2

- -10.3

Fractional integers are limited to -16384.0 to +16383.9999.

<a id="AN_OVERVIEW_STRINGS"></a>
#### Strings

Strings may be given in one of two formats.

- ASCII with the facility for special characters (e.g. tab, carriage return, line feed) to be specified via escape sequences. ASCII strings must be enclosed in double quotes (").

- Hexadecimal string, a stream of two-digit hexadecimal values. Hexadecimal strings must be enclosed within square brackets (\[ \]). Please note that each 'byte' being transferred must be specified using two digits - for instance the byte value '2' would be represented '02'.

**In the case of an ASCII string, the following characters will be escaped:**

<table>
<tbody>
<tr>
<td>Null</td>
<td>\0</td>
</tr>
<tr>
<td>Horizontal Tab</td>
<td>\t</td>
</tr>
<tr>
<td>Backslash</td>
<td>\\</td>
</tr>
<tr>
<td>Double Quotes</td>
<td>\\</td>
</tr>
<tr>
<td>Carriage Return</td>
<td>\r</td>
</tr>
<tr>
<td>Linefeed</td>
<td>\n</td>
</tr>
<tr>
<td>Terminal Bell</td>
<td>\a</td>
</tr>
<tr>
<td>Backspace</td>
<td>\b</td>
</tr>
<tr>
<td>Vertical Tab</td>
<td>\v</td>
</tr>
<tr>
<td>Form feed</td>
<td>\f</td>
</tr>
<tr>
<td>Escape</td>
<td>\e</td>
</tr>
</tbody>
</table>

Examples:

- "hello" ASCII string representation of hello

- "\r\nNew line" ASCII string representation of \<CR\>\<LF\>New line

- \[68656c6c6f\] Hex string representation of hello

An empty string will be represented as either an empty ASCII string ("") or an empty hexadecimal string (\[\]). Both representations are valid and equivalent for input, for output only the (\[\]) form will be used.

#### Raw Binary

Raw binary can be useful for transferring data that is either transmitted or received over the network. Only a limited number of commands support this format. Binary transfers are achieved by the DCE leaving terminal mode and remaining in raw mode until one of the following conditions is met:

1.  A pre-specified number of bytes has been exchanged between DTE and DCE

2.  An 'escape sequence' of three consecutive '+' characters has been sent from the DTE to the DCE

> [!NOTE]
> The 'escape sequence' method for returning to terminal mode relies not only on receipt of the '+++' sequence, but also the absence of any further input for a period of time. By default this is 1 second.

#### Raw Binary - From DCE to DTE

For retrieval of data in binary mode the DTE must either specify the number of bytes it wishes to receive or specify zero to request a persistent exit from terminal mode. On leaving terminal mode, the DCE will output a single '#' character, it will then transmit data in raw binary format.

The DCE will return to terminal mode if either of the following occurs:

1.  The +++ escape sequence is received from the DTE

2.  The number of bytes requested by the DTE has been sent

3.  All available data has been sent to the DTE (e.g. DTE asks for 10 bytes but only 5 are available for reading)

On returning to terminal mode, the DCE will return the result of the command which initiated the transfer.

#### Raw Binary - From DTE to DCE

For transmission of data in binary mode the DTE must either specify the number of bytes it wishes to send to the DCE or specify zero to request a persistent exit from terminal mode. On leaving terminal mode, the DCE will accept binary format data until such time as:

1.  The +++ escape sequence is received from the DTE

2.  The number of bytes requested by the DTE has been sent

When operating in non-terminal mode, the DCE will periodically flush (i.e. transmit) the accumulated data. Generally, this means writing the data to an associated socket. The time period for the automatic flush of data is configurable (please see the XXX command).

---
### Command Input

Commands consist of the following:

- Must start with 'AT'

- Zero or more basic commands

- Zero or one extended commands

- Terminate with \<CR\>\<LF\>

#### Basic Commands:

Basic commands are single alphabetic characters which may be preceded by a single '&' character. An optional single numeric argument may then follow.

#### Extended Commands:

Extended commands begin with a single '+' character followed by a command name. If the command requires parameters, the command name is followed by a single '=' character with each parameter separated from the next by a comma. Parameters must follow the formatting rules for Integers, String or Labels.

Examples:

<table>
<tbody>
<tr>
<td><code>ATL&lt;CR&gt;&lt;LF&gt;</code></td>
<td>Basic command 'L'</td>
</tr>
<tr>
<td><code>ATJ0&lt;CR&gt;&lt;LF&gt;</code></td>
<td>Basic command 'J' with argument '0'</td>
</tr>
<tr>
<td><code>ATLJ0&lt;CR&gt;&lt;LF&gt;</code></td>
<td>Basic command 'L' and 'J' with argument '0'</td>
</tr>
<tr>
<td><code>AT+CMD&lt;CR&gt;&lt;LF&gt;</code></td>
<td>Extended command 'CMD'</td>
</tr>
<tr>
<td><code>AT+CMD=0&lt;CR&gt;&lt;LF&gt;</code></td>
<td>Extended command 'CMD' with single parameter '0'</td>
</tr>
<tr>
<td><code>AT+CMD=0,1&lt;CR&gt;&lt;LF&gt;</code></td>
<td>Extended command 'CMD' with two parameters '0' and '1'</td>
</tr>
<tr>
<td><code>ATJ0+CMD=0,1&lt;CR&gt;&lt;LF&gt;</code></td>
<td>Combination of basic and extended commands</td>
</tr>
</tbody>
</table>

#### Output

Before transmitting token/parameter data to the DTE, the DCE will inspect each element to determine if any of the bytes would render inconsistently on a terminal display. In such cases, the element will be returned in hexadecimal format. This allows, for example, UTF-8 formatted SSIDs to be sent to a DTE in a fashion suitable for re-use, i.e. a human using a terminal application can copy this data and use it as a parameter in a command. Where multiple pieces of information are being returned, the DCE will comma separate each token.

Examples:

    A<CR><LF>B"C\D<TAB>E            "A\r\nB\"C\\D\tE"
    A©B                             [41C2A942]

<a id="_configuration_commands"></a>
### Configuration Commands

Certain commands are used to configure or query parts of the DCE. These commands allow the DTE to set new parameter values and get existing parameter values. The commands can query all parameter values, query a single parameter ID, or set a single parameter ID.

Each configuration parameter will consist of an ID and a value.

Commands can have preceding arguments which are specific to that particular command, but the ID and value arguments will be the last arguments.

For example:

    AT+SOMECFGCMD=<CMD_SPEC_ARG>                - Get all parameters
    AT+SOMECFGCMD=<CMD_SPEC_ARG>,<ID>           - Get single parameter
    AT+SOMECFGCMD=<CMD_SPEC_ARG>,<ID>,<VALUE>   - Set single parameter

#### Single Value Parameters:

These parameters may have only one value and are accessed using the parameter ID.

#### Multiple Value Parameters:

These parameters may have more than one value.

When reading all values, the parameter ID can be used, however when accessing a single value within the set of all values the command will use a fractional integer form of the ID consisting of \<ID\>.\<INDEX\>

Reading all parameter values
<a id="EXAMPLE_ReadAllParamVal"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"value1"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"value2"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.2,"value3"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

To read a single value
<a id="EXAMPLE_ReadSingleVal"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD=5.1</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"value2"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

When writing a value, the behavior will depend on the implementation of the command, however often writing a value to the parameter \<ID\> will cause an additional value to be appended to the set of parameter values, writing to the fractional \<ID\>.\<INDEX\> will cause that parameter index to be updated.

To set an additional value
<a id="EXAMPLE_SetAddVal"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"value1"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD=5,"newvalue"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"value1"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"newvalue"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

To replace an existing value
<a id="EXAMPLE_ReplaceAddVal"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"value1"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"value2"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD=5.0,"newvalue"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"newvalue"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"value2"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

In addition to the fractional integer form a command response may include a range indication primarily to indicate how many valid responses will follow. This optional response will only be present if the parameter implements it and the request was to read all values, it will not be present if a request for a single value was made using a fractional integer ID.

The format of the range indication uses the non-fractional ID of the parameter and a single integer value:

This example indicates that +CMD parameter ID 5 will return 2 values, 5.0 and 5.1:

Range of IDs
<a id="EXAMPLE_ValIDRange"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5,2</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"value1"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"value2"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

#### Query Response Elements:

Standard configuration parameter queries return a simple \<ID\>,\<VALUE\> pair. For single value parameters the \<ID\> will be an integer, for multiple value parameters the \<ID\> will be a fractional integer in the form \<ID\>.0, \<ID\>.1 etc for each value.

Simple ID/Value
<a id="EXAMPLE_SimpleIDVal"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"simple1"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"simple2"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

#### Complex Value Elements:

When queried some configuration parameters will return a more complex value in place of the \<VALUE\> element of the response. A complex value is more than one comma separated value.

Complex ID/Value
<a id="EXAMPLE_ComplexIDVal"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD=5</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.0,"complex11","complex12","complex12"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:5.1,"complex21","complex22","complex22"</code></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

#### Default Configurations and Presets:

Configuration commands are initially loaded with default values, also known as **preset 0**. Many configuration commands also support reloading preset values.

The reserved \<ID\> value 0 is used to query and load configuration command presets. Querying this \<ID\> will return the current base preset used to load the configuration commands values. Setting this \<ID\>'s value will load a preset set of values.

> [!NOTE]
> Currently only **preset 0** is defined to be the default system values. Other presets may be defined in future.

> [!NOTE]
> The queried preset indicates the preset last used to load the values in the configuration command, subsequent changes may have occurred to individual values. Therefore it does not indicate that any particular value is currently set to that preset value, only that it initially was.

Using preset 0
<a id="EXAMPLE_Preset0IDVal"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><code>AT+CMD</code></td>
<td>Query all values</td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:1,1234</code></td>
<td>&lt;ID&gt; 1 default values is 1234</td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:2,"A String"</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD=1,5678</code></td>
<td>Set &lt;ID&gt; 1 to be 5678</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD</code></td>
<td>Query all values</td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:1,5678</code></td>
<td>&lt;ID&gt; 1 now changed to 5678</td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:2,"A String"</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD=0</code></td>
<td>Query current base preset</td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:0,0</code></td>
<td>Current preset is 0, default values</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD=0,0</code></td>
<td>Load preset 0 in to command values</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>AT+CMD</code></td>
<td>Query all values</td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:1,1234</code></td>
<td>&lt;ID&gt; 1 returned to default value</td>
</tr>
<tr>
<td>←</td>
<td><code>+CMD:2,"A String"</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="_security_model"></a>
### Security Model

Security is based around a combination of privilege levels and profiles. Various elements in the system are assigned a security descriptor which describes the minimum privilege level required to access the element for a given profile.

#### Profiles

Up to four profiles can be defined in the system. Each profile defines a set of functionality which is accessible for a given access path.

For example, one profile may be assigned to all accesses via a local physical interface (UART, I2C, SPI etc) while a second profile is assigned to all accesses via a remote interface (Sockets). This allows different privilege requirements to be specified depending on how the system is accessed, locally vs remotely.

#### Privilege Level

There are four defined privilege levels:

- Guest

- User

- Super-user

- Root

Guest having the lowest privilege while Root has the highest. Any element can be accessed by a user with a privilege level of 'at least' what is specified in its security descriptor for the current access profile.

#### Security Descriptor

Elements in the system are assigned a security descriptor, this consists of a minimum user privilege level for each of the four profiles. In this documentation these descriptors are shown as four characters, each character can be either `G`(uest), `U`(ser), `S`(uper-user) or `R`(oot).

For example, the descriptor `GSRG` means:

- Profile 1 - Guest

- Profile 2 - Super-user

- Profile 3 - Root

- Profile 4 - Guest

---
<a id="_status_response_codes"></a>
## Status Response Codes

| Value | Name | Description |
|----|----|----|
| 0,0 | OK | OK |
| 0,1 | ERROR | General Error |
| 0,2 | INVALID_CMD | Invalid AT Command |
| 0,3 | UNKNOWN_CMD | Unknown AT Command |
| 0,4 | INVALID_PARAMETER | Invalid Parameter |
| 0,5 | INCORRECT_NUM_PARAMS | Incorrect Number of Parameters |
| 0,6 | STORE_UPDATE_BLOCKED | Configuration Update Blocked |
| 0,7 | STORE_ACCESS_FAILED | Configuration Access Failed |
| 0,8 | TIMEOUT | Command Timed Out |
| 0,9 | HOST_INTERFACE_FAILED | Host Interface Failed |
| 0,10 | ACCESS_DENIED | Access Denied |
| 0,11 | CONFIG_CONFLICT | Configuration Conflict |

CORE Status Codes (Module ID = 0)

 

| Value | Name | Description |
|----|----|----|
| 1,0 | WIFI_API_REQUEST_FAILED | Wi-Fi Request Failed |
| 1,1 | STA_NOT_CONNECTED | STA Not Connected |
| 1,2 | NETWORK_ERROR | Network Error |
| 1,3 | FILE_SYSTEM_ERROR | File System Error |

[SYSTEM](#AN_MOD_SYSTEM) Status Codes (Module ID = 1)

 

| Value | Name | Description |
|----|----|----|
| 3,0 | CFG_NOT_PRESENT | Configuration not present |

[CFG](#AN_MOD_CFG) Status Codes (Module ID = 3)

 

| Value | Name | Description |
|----|----|----|
| 5,0 | DNS_TYPE_NOT_SUPPORTED | DNS Type Not Supported |
| 5,1 | DNS_TIMEOUT | DNS Query Timeout |
| 5,2 | DNS_ERROR | DNS Error |
| 5,3 | DNS_RECORD_NOT_FOUND | DNS Record Not Found |
| 5,4 | DNS_NON_EXISTENT_DOMAIN | DNS Non-Existent Domain |
| 5,5 | DNS_AUTH_DATA_ERROR | DNS Data Authentication Error |
| 5,6 | DNS_TRUNCATED_RESPONSE | DNS Response Truncated |

[DNS](#AN_MOD_DNS) Status Codes (Module ID = 5)

 

| Value | Name | Description |
|----|----|----|
| 7,0 | TSFR_PROTOCOL_NOT_SUPPORTED | Unsupported File Transfer Protocol |
| 7,1 | FILE_EXISTS | File Exists |
| 7,2 | FILE_NOT_FOUND | File Not Found |
| 7,3 | INVALID_FILE_TYPE | Invalid File Type |
| 7,4 | FILE_CREATE_FAILED | File create failed |
| 7,5 | FILE_WRITE_FAILED | File write failed |

[FS](#AN_MOD_FS) Status Codes (Module ID = 7)

 

| Value | Name                                               | Description |
|-------|----------------------------------------------------|-------------|
| 8,0   | MQTT_ERROR | MQTT Error  |

[MQTT](#AN_MOD_MQTT) Status Codes (Module ID = 8)

 

| Value | Name | Description |
|----|----|----|
| 9,0 | NETWORK_INTF_DOWN | Network interface down |

[NETIF](#AN_MOD_NETIF) Status Codes (Module ID = 9)

 

| Value | Name | Description |
|----|----|----|
| 10,0 | ERASE_DONE | Erase Done |
| 10,1 | WRITE_DONE | Write Done |
| 10,2 | VERIFY_DONE | Verify Done |
| 10,3 | ACTIVATE_DONE | Activate Done |
| 10,4 | INVALIDATE_DONE | Invalidate Done |
| 10,5 | OTA_ERROR | OTA Error |
| 10,6 | OTA_NO_STA_CONN | No STA Connection |
| 10,7 | OTA_PROTOCOL_ERROR | Protocol Error |
| 10,8 | OTA_TLS_ERROR | TLS Error |
| 10,9 | OTA_IMG_TOO_LARGE | Image Exceeds |
| 10,10 | OTA_TIMEOUT | Timeout |
| 10,11 | OTA_VERIFY_FAILED | Image Verify Failed |

[OTA](#AN_MOD_OTA) Status Codes (Module ID = 10)

 

| Value | Name                                                 | Description |
|-------|------------------------------------------------------|-------------|
| 11,0  | PING_FAILED | Ping Failed |

[PING](#AN_MOD_PING) Status Codes (Module ID = 11)

 

| Value | Name | Description |
|----|----|----|
| 13,0 | SNTP_SERVER_TMO | NTP Server Timeout |
| 13,1 | SNTP_PROTOCOL_ERROR | NTP Protocol Error |

[SNTP](#AN_MOD_SNTP) Status Codes (Module ID = 13)

 

| Value | Name | Description |
|----|----|----|
| 14,0 | SOCKET_ID_NOT_FOUND | Socket ID Not Found |
| 14,1 | LENGTH_MISMATCH | Length Mismatch |
| 14,2 | NO_FREE_SOCKETS | No Free Sockets |
| 14,3 | SOCKET_INVALID_PROTOCOL | Invalid Socket Protocol |
| 14,4 | SOCKET_CLOSE_FAILED | Socket Close Failed |
| 14,5 | SOCKET_BIND_FAILED | Socket Bind Failed |
| 14,6 | SOCKET_TLS_FAILED | Socket TLS Failed |
| 14,7 | SOCKET_CONNECT_FAILED | Socket Connect Failed |
| 14,8 | SOCKET_SEND_FAILED | Socket Send Failed |
| 14,9 | SOCKET_SET_OPT_FAILED | Socket Set Option Failed |
| 14,10 | SOCKET_REMOTE_NOT_SET | Socket Destination Not Set |
| 14,11 | MULTICAST_ERROR | Multicast Error |
| 14,12 | SOCKET_NOT_READY | Socket Not Ready |
| 14,13 | SOCKET_SEQUENCE_ERROR | Socket Sequence Error |

[SOCKET](#AN_MOD_SOCKET) Status Codes (Module ID = 14)

 

| Value | Name                                               | Description |
|-------|----------------------------------------------------|-------------|
| 16,0  | TIME_ERROR | Time Error  |

[TIME](#AN_MOD_TIME) Status Codes (Module ID = 16)

 

| Value | Name | Description |
|----|----|----|
| 17,0 | TLS_CA_CERT_MISSING | CA Cert Missing |
| 17,1 | TLS_CA_CERT_VALIDATION | CA Cert Validation |
| 17,2 | TLS_CA_CERT_DATE_VALIDATION | CA Cert Date Validation |
| 17,3 | TLS_KEY_PAIR_INCOMPLETE | Key Pair Incomplete |
| 17,4 | TLS_PEER_DOMAIN_MISSING | Peer Domain Missing |

[TLS](#AN_MOD_TLS) Status Codes (Module ID = 17)

 

| Value | Name | Description |
|----|----|----|
| 18,0 | WAP_STOP_REFUSED | Soft AP Stop Not Permitted |
| 18,1 | WAP_STOP_FAILED | Soft AP Stop Failed |
| 18,2 | WAP_START_REFUSED | Soft AP Start Not Permitted |
| 18,3 | WAP_START_FAILED | Soft AP Start Failed |
| 18,4 | UNSUPPORTTED_SEC_TYPE | Unsupported Security Type |

[WAP](#AN_MOD_WAP) Status Codes (Module ID = 18)

 

| Value | Name | Description |
|----|----|----|
| 20,0 | STA_DISCONN_REFUSED | STA Disconnect Not Permitted |
| 20,1 | STA_DISCONN_FAILED | STA Disconnect Failed |
| 20,2 | STA_CONN_REFUSED | STA Connection Not Permitted |
| 20,3 | STA_CONN_FAILED | STA Connection Failed |

[WSTA](#AN_MOD_WSTA) Status Codes (Module ID = 20)

 

| Value | Name | Description |
|----|----|----|
| 22,0 | ASSOC_NOT_FOUND | Association Not Found |

[ASSOC](#AN_MOD_ASSOC) Status Codes (Module ID = 22)

 

| Value | Name | Description |
|----|----|----|
| 29,0 | NVM_LOCKED | NVM Locked Until Reset |

[NVM](#AN_MOD_NVM) Status Codes (Module ID = 29)

 

| Value | Name | Description |
|----|----|----|
| 30,0 | <span id="AN_STATUS_DFU_ADDRESS_WARNING"></span> DFU_ADDRESS_WARNING | No Bootable Image In Other Partition |

[DFU](#AN_MOD_DFU) Status Codes (Module ID = 30)

 

| Value | Name | Description |
|----|----|----|
| 31,0 | PPS_WIFI_PS_NOT_ENABLED | Wi-Fi PS Not Enabled |
| 31,1 | PPS_TIMEOUT | PPS Timeout |
| 31,2 | PPS_PAUSE_EXPIRED | PPS Pause Expired |

[PPS](#AN_MOD_PPS) Status Codes (Module ID = 31)

 

| Value | Name | Description |
|----|----|----|
| 33,0 | ARB_NO_INCREASE | The Value Provided Would Not Increase The ARB |
| 33,1 | ARB_REJECTED | The Value Provided Would Invalidate The Current Image |

[ARB](#AN_MOD_ARB) Status Codes (Module ID = 33)

 

| Value | Name | Description |
|----|----|----|
| 34,0 | HTTP_DNS_FAILED | HTTP DNS failed |
| 34,1 | HTTP_TLS_FAILED | HTTP TLS failed |
| 34,2 | HTTP_CONNECT_FAILED | HTTP connect failed |
| 34,3 | HTTP_MEMORY | HTTP buffer allocation |
| 34,4 | HTTP_RESPONSE_HEADERS | HTTP response format |
| 34,5 | HTTP_RECV_FAILED | HTTP receive failed |
| 34,6 | HTTP_SEND_FAILED | HTTP send failed |
| 34,7 | HTTP_TIMEOUT | HTTP timeout |

[HTTP](#AN_MOD_HTTP) Status Codes (Module ID = 34)

 

---
## Serial Interface

### Basic Commands

#### E

##### Description

This command controls if characters received from the DTE are echoed back to the DTE.

| Command  | Description |
|----------|-------------|
| ATE\<N\> | Set value   |

**Command Syntax:**

<table>
<caption>Command Parameter Syntax:</caption>
<colgroup>
<col style="width: 18%" />
<col style="width: 18%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;N&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Echo control<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Turn off character echo.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Turn on character echo.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### F

##### Description

This command controls numeric, string and data formats.

The formatting control determines how integer, string and byte arrays are displayed.

**This value is built up from three values:**

<table>
<tbody>
<tr>
<td>Bit Mask</td>
<td>Control Value</td>
</tr>
<tr>
<td>0b00000011</td>
<td>String/Byte Array Control</td>
</tr>
<tr>
<td>0b00000100</td>
<td>Integer Number Base Support</td>
</tr>
<tr>
<td>0b00001000</td>
<td>Default Number Base</td>
</tr>
</tbody>
</table>

The default value for this is 0b00000111 (7).

###### String/Byte Array Control:

By default, string and byte arrays are displayed using safe-strings where possible or hexadecimal strings, see [Strings](#AN_OVERVIEW_STRINGS).

If the data contains only printable ASCII characters it will be displayed as a string.

If the data contains non-printable ASCII characters which could be displayed as escaped sequences it will be displayed as a string with escape sequences.

If the data contains non-printable ASCII characters which can’t be displayed as escaped sequences it will be displayed as a hexadecimal string.

<table>
<colgroup>
<col style="width: 50%" />
<col style="width: 50%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Control Value</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Both string and byte arrays are displayed as hexadecimal strings.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Byte arrays are displayed as hexadecimal strings.</p>
<p>Strings are displayed as ASCII strings unless they contain non-printable characters, escape characters will not be used. Non-printable characters will result in a hexadecimal string being used.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Byte arrays are displayed as hexadecimal strings.</p>
<p>Strings are displayed as ASCII strings unless they contain non-printable characters, escape characters will be used if possible, otherwise as a hexadecimal string.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Both byte arrays and strings are displayed as strings using escape sequences if possible, otherwise hexadecimal strings.</p></td>
</tr>
</tbody>
</table>

###### Integer Number Base Support

The Integer Number Base Support bit determines if number bases other then the default are supported. If this bit is set support is enabled.

###### Default Number Base

The Default Number Base determines if decimal or hexadecimal numbers are used by default for integers. If this bit is set the default number base will be hexadecimal, otherwise decimal is used.

| Command  | Description |
|----------|-------------|
| ATF\<N\> | Set value   |

**Command Syntax:**

<table>
<caption>Command Parameter Syntax:</caption>
<colgroup>
<col style="width: 18%" />
<col style="width: 18%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;N&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Format control<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Hex strings only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Hex bytes, basic strings.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Hex bytes, escaped strings.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Escaped strings or hex bytes.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Number base support.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>Default to hex integers.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### M

##### Description

**This command controls the command/response mode.**

| Command  | Description |
|----------|-------------|
| ATM\<N\> | Set value   |

**Command Syntax:**

<table>
<caption>Command Parameter Syntax:</caption>
<colgroup>
<col style="width: 18%" />
<col style="width: 18%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;N&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Command mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Verbose string mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Numeric mode.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### V

##### Description

This command controls the level of verbosity used when display command responses. The response to this command will be in the new verbosity format specified.

| Command  | Description |
|----------|-------------|
| ATV\<N\> | Set value   |

**Command Syntax:**

<table>
<caption>Command Parameter Syntax:</caption>
<colgroup>
<col style="width: 18%" />
<col style="width: 18%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;N&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Verbosity level<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Just 0 or 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>0 for success, 1:&lt;STATUS_CODE&gt; for error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Just OK or ERROR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>OK for success, ERROR:&lt;STATUS_CODE&gt; for error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>OK for success, either ERROR:&lt;STATUS_MSG&gt; or ERROR:&lt;STATUS_CODE&gt; for error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>OK for success, ERROR:&lt;STATUS_CODE&gt;[,&lt;STATUS_MSG&gt;] for error.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### &K

##### Description

**This command controls is used to select the local flow control method.**

| Command   | Description |
|-----------|-------------|
| AT&K\<N\> | Set value   |

**Command Syntax:**

<table>
<caption>Command Parameter Syntax:</caption>
<colgroup>
<col style="width: 18%" />
<col style="width: 18%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;N&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Flow control<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>All flow control is disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>RTS/CTS flow control is enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
---
<a id="AN_MOD_SYSTEM"></a>
## SYSTEM (Module ID = 1)

### AEC Reference:

#### +BOOT

##### Description

**System has booted.**

| AEC              | Description |
|------------------|-------------|
| +BOOT:\<BANNER\> | System boot |

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
<td style="text-align: left;"><p>&lt;BANNER&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Boot banner<br />
</p></td>
</tr>
</tbody>
</table>

---
## INTERNAL (Module ID = 2)

### Command Reference:

#### +GMI

##### Description

This command requests manufacturer identification.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+GMI</p></td>
<td style="text-align: left;"><p>Query the manufacturers ID/name<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

| Response        | Description          |
|-----------------|----------------------|
| +GMI:\<MAN_ID\> | Information Response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Manufacturers ID/name<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +GMM

##### Description

This command requests model identification.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+GMM</p></td>
<td style="text-align: left;"><p>Query the model information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

| Response          | Description          |
|-------------------|----------------------|
| +GMM:\<MODEL_ID\> | Information Response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Model information<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +GMR

##### Description

This command requests revision identification.

**Version Information Format**

"2.0.0 0 ab12cdef1 \[12:34:56 Feb 01 2024\]"

The version information string is constructed from:

- Software version MAJOR.MINOR.PATCH

- Security version

- Software hash identifier

- Build date

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+GMR</p></td>
<td style="text-align: left;"><p>Query the revision information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

| Response              | Description          |
|-----------------------|----------------------|
| +GMR:\<VERSION_INFO\> | Information Response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Version information<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +IPR

##### Description

This command sets the DTE serial port baud rate.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+IPR</p></td>
<td style="text-align: left;"><p>Query the current baud rate<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+IPR=&lt;BAUD_RATE&gt;</p></td>
<td style="text-align: left;"><p>Set the serial baud rate<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;BAUD_RATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Baud rate<br />
<br />
Positive unsigned 32-bit value<br />
</p></td>
</tr>
</tbody>
</table>

| Response           | Description          |
|--------------------|----------------------|
| +IPR:\<BAUD_RATE\> | Information Response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>&lt;BAUD_RATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Baud rate<br />
<br />
Positive unsigned 32-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
---
<a id="AN_MOD_CFG"></a>
## CFG (Module ID = 3)

### Command Reference:

#### +CFG

##### Description

This command is used to read or set the system configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+CFG</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+CFG=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+CFG=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response            | Description   |
|---------------------|---------------|
| +CFG:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;DEVICE_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>The device name<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;VERSION&gt;</p></td>
<td style="text-align: left;"><p>Fractional Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Software version number<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>&lt;PATCH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Software patch number<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>&lt;SECURITY&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Security value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>&lt;BUILD_HASH&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Build ID<br />
Maximum length of string is 5<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>&lt;BUILD_TIME&gt;</p></td>
<td style="text-align: left;"><p>UTC Time<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Build time<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>&lt;CMD_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Command port<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UART1.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>&lt;CMD_BAUD&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Command baud rate<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>&lt;CMD_TIMEOUT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Command baud rate change timeout (ms)<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_CFG_STORE_ID_ARCHIVE_FILTER"></span> 50</p></td>
<td style="text-align: left;"><p>&lt;ARCHIVE_FILTER&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Archive filter<br />
Maximum length of string is 32<br />
This is a multiple value parameter<br />
with an ID range 50.0 to 50.7<br />
</p>
<p>The filter is a list of command IDs either in string form (<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>) or integer form (0x1400).</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_CFG_STORE_ID_ARCHIVE_SLOTS"></span> 51</p></td>
<td style="text-align: left;"><p>&lt;ARCHIVE_SLOTS&gt;</p></td>
<td style="text-align: left;"><p>UTC Time<br />
</p></td>
<td style="text-align: left;"><p>Archive slots<br />
This is a multiple value parameter<br />
with an ID range 51.1 to 51.2<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>52</p></td>
<td style="text-align: left;"><p>&lt;AUTOEXEC_STATUS&gt;</p></td>
<td style="text-align: left;"><p>Status<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Auto-execute status<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>100</p></td>
<td style="text-align: left;"><p>&lt;DEBUG_PORT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Debug port<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UART1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>UART2.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>101</p></td>
<td style="text-align: left;"><p>&lt;DEBUG_BAUD&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Debug baud rate<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_CFG_CFGCP"></a>
#### +CFGCP

##### Description

This command is used to copy configurations to/from storage.

Configurations managed by [+CFGCP](#AN_CMD_AT_CFG_CFGCP) are groups of configuration command parameters. The command allows these parameters to be saved to either flash files or archive slots in memory for later retrival.

[+CFGCP](#AN_CMD_AT_CFG_CFGCP) supports:

- Saving active configurations to flash files

- Saving active configurations to in memory archive slots

- Restoring flash files to active configuration

- Restoring flash files to in memory archive slots

- Restoring in memory archive slots to active configurations

- Duplicating in memory archive slots

> [!NOTE]
> Only parameter tables of configuration commands which have been changed are stored to flash files or archive slots.

**Active Configuration**

The active configuration is considered to occupy slot 0 for the purposes of the source and destination of [+CFGCP](#AN_CMD_AT_CFG_CFGCP).

**Archive Slots**

Archive slots are numbered 1+, they represent in memory holding locations for configuration sets. The parameters in these slots are not active and not maintained through reset.

Slots can be queried through [ARCHIVE_SLOTS](#AN_CMD_CFG_STORE_ID_ARCHIVE_SLOTS), these parameters contain the timestamp of the configuration set when stored from an active configuration.

A slot can be emptied by writing a zero value to the appropriate index within [ARCHIVE_SLOTS](#AN_CMD_CFG_STORE_ID_ARCHIVE_SLOTS).

**Archive Filters**

The [ARCHIVE_FILTER](#AN_CMD_CFG_STORE_ID_ARCHIVE_FILTER) contains a list of command IDs which are filtered out when storing or loading a configuration set. This allows a partial configuration to be stored or restored.

**Archive Files**

Configurations are stored in 'Configuration Files' types which can be queried and deleted through [+FS](#AN_CMD_AT_FS_FLFS_FS).

**Configuration Summary**

The response to [+CFGCP](#AN_CMD_AT_CFG_CFGCP) is a summary list of command IDs with the number of command elements being stored or restored and the total size of the memory used for that command.

**Auto-Execute Configuration**

If a configuration is stored to an archive file called 'autoexec' it will be automatically loaded during device boot, before a command prompt is presented.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+CFGCP=&lt;CFGSRC&gt;,&lt;CFGDST&gt;</p></td>
<td style="text-align: left;"><p>Copy configuration<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CFGSRC&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Configuration source<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CFGDST&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Configuration destination<br />
</p></td>
</tr>
</tbody>
</table>

| Response                                     | Description |
|----------------------------------------------|-------------|
| +CFGCP:\<CMD_ID\>,\<NUM_ITEMS\>,\<ITEM_LEN\> | copy event  |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration command ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;NUM_ITEMS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of items<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ITEM_LEN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length of items<br />
</p></td>
</tr>
</tbody>
</table>

---
---
### Examples:

Saving active configuration to storage
<a id="EXAMPLE_dc6130cfe9a84137759d254f2f775e9c95a1a939"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=1,"SSID"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=2,3</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=3,"Password"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NETIF_NETIFC">+NETIFC</a>=0,20,1</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSC">+DNSC</a>=1,"1.1.1.1"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSC">+DNSC</a>=2,0</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>=0,"saved"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>:0x0500,3,49</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>:0x0900,11,182</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>:0x1400,10,136</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

Restoring configuration from storage
<a id="EXAMPLE_52043c5b1266965e87fee1d62cf0473db94a8a9f"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>="saved",0</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>:0x0500,3,49</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>:0x0900,11,182</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_CFG_CFGCP">+CFGCP</a>:0x1400,10,136</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

---
## DHCP (Module ID = 4)

### Command Reference:

#### +DHCPSC

##### Description

This command is used to read or set the DHCP server configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+DHCPSC</p></td>
<td style="text-align: left;"><p>Query pool list<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+DHCPSC=&lt;IDX&gt;</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+DHCPSC=&lt;IDX&gt;,&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+DHCPSC=&lt;IDX&gt;,&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;IDX&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Pool index<br />
<br />
Value is 0<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response               | Description   |
|------------------------|---------------|
| +DHCPSC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;ENABLED&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>DCE’s internal DHCP Server<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;POOL_START&gt;</p></td>
<td style="text-align: left;"><p>IPv4 Address<br />
</p></td>
<td style="text-align: left;"><p>Start address of DHCP server pool<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is 'a.b.c.d'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;POOL_END&gt;</p></td>
<td style="text-align: left;"><p>IPv4 Address<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>End address of DHCP server pool<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is 'a.b.c.d'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;POOL_LEASES&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Number of leases<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>&lt;NETIF_IDX&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Network interface index<br />
<br />
Valid range is 0 to 1<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;GATEWAY&gt;</p></td>
<td style="text-align: left;"><p>IPv4 Address<br />
</p></td>
<td style="text-align: left;"><p>The address of the default gateway<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is 'a.b.c.d'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
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

1.  Manually configured via [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_SVR](#AN_CMD_DNSC_STORE_ID_DNS_SVR).

2.  Automatically configured via IPv4 DHCP option 6.

3.  Automatically configured via IPv6 Router Advertisement RNDSS.

Switching between manual and automatic configuration is performed by [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_AUTO](#AN_CMD_DNSC_STORE_ID_DNS_AUTO).

#### Resource Queries

The supported query types are listed in [+DNSRESOLV](#AN_CMD_AT_DNS_DNSRESOLV) parameter [TYPE](#AN_CMD_AT_DNS_DNSRESOLV_TYPE), other types may be specified as well. For unknown type the [+DNSRESOLV](#AN_AEC_AT_DNS_DNSRESOLV) response will simply include the undecoded RR data.

The DNS query ANY is indirectly supported, it has generally been deprecated as a DNS query type and some servers do not respond to it. If the ANY query is specified the DCE will generate two separate queries for A and AAAA records. When generating the queries for ANY, the DCE will use the configuration of [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_PROTO_PREF](#AN_CMD_DNSC_STORE_ID_DNS_PROTO_PREF) to determine selection and order of A and AAAA queries.

> [!NOTE]
> [DNS_PROTO_PREF](#AN_CMD_DNSC_STORE_ID_DNS_PROTO_PREF) specifies the order of queries made, it does not control the order of responses received.

#### Reverse Address Queries

IP address to name queries can be made using a **PTR** (12) query in the form:

- \<IPv4 Addr\>.in-addr.arpa

- \<IPv6 Addr\>.ip6.arpa

---
#### Connection Types

The DNS modules supports UDP, TCP, TLS and Multicast-UDP for performing DNS queries.

The default connection method is to use UDP to port 53 of the servers configured either manually or through DHCP/RA.

##### DNS over UDP

For queries to be sent via UDP [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_CONN_PREF](#AN_CMD_DNSC_STORE_ID_DNS_CONN_PREF) must be set to 0 (UDP/TLS). All connections to the configured servers will now be via UDP.

The UDP port on the server used for queries will be set by [DNS_SRV_PORT](#AN_CMD_DNSC_STORE_ID_DNS_SRV_PORT) which defaults to 53.

##### DNS over TCP

For queries to be sent via TCP [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_CONN_PREF](#AN_CMD_DNSC_STORE_ID_DNS_CONN_PREF) must be set to 1 (TCP/TLS). All connections to the configured servers will now be via TCP.

The TCP port on the server used for queries will be set by [DNS_SRV_PORT](#AN_CMD_DNSC_STORE_ID_DNS_SRV_PORT) which defaults to 53.

Option [DNS_CONN_IDLE_TIMEOUT](#AN_CMD_DNSC_STORE_ID_DNS_CONN_IDLE_TIMEOUT) can be used to set an idle timeout, the DNC module will request the IDLE timeout from the DNS server and honour that time period.

##### DNS over TLS

For queries to be sent via TLS [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_CONN_PREF](#AN_CMD_DNSC_STORE_ID_DNS_CONN_PREF) must be set to 1 (TCP/TLS). All connections to the configured servers will now be via TLS.

The TLS port on the server used for queries will be set by [DNS_SRV_SECURE_PORT](#AN_CMD_DNSC_STORE_ID_DNS_SRV_SECURE_PORT) which defaults to 853.

Option [DNS_CONN_IDLE_TIMEOUT](#AN_CMD_DNSC_STORE_ID_DNS_CONN_IDLE_TIMEOUT) can be used to set an idle timeout, the DNC module will request the IDLE timeout from the DNS server and honour that time period.

---
#### DNSSEC Support

Support for DNSSEC is configured by [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_DNSSEC_MODE](#AN_CMD_DNSC_STORE_ID_DNS_DNSSEC_MODE) which offers three possible modes of operation:

1.  No support, the DO bit of EDNS0 extended flags is not set indicating that the DCE is unaware of DNSSEC operations.

2.  DNSSEC aware, this sets the DO bit of EDNS0 extended flags to indicate that DNSSEC RRs should be sent in response to queries. These RRs will be past the to DTE for further processing.

3.  DNSSEC authenticated answer only. In addition to the previous state the DNS module will not process any query responses which do not have either the AA bit set (indicating the DNS server is an authority for the domain) or the AD bit set (indicating the server has authenticated the response).

#### Cache Control

Query responses are held in a small answer cache to speed up further queries. Records are held in the cache based on the TTL value specified in the records. In addition the DTE can set a cache timeout via [+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_CACHE_TTL](#AN_CMD_DNSC_STORE_ID_DNS_CACHE_TTL) which, if lower than a response TTL, will override it causing records to be expired from the cache sooner.

#### MDNS Support

In addition to unicast DNS queries the DNS module supports multicast queries for those records in the **.local** domain.

[+DNSC](#AN_CMD_AT_DNS_DNSC) option [DNS_MC_SRV_PREF](#AN_CMD_DNSC_STORE_ID_DNS_MC_SRV_PREF) configures if either or both IPv4 and IPv6 multicast queries should be made. If [DNS_MC_SRV_PREF](#AN_CMD_DNSC_STORE_ID_DNS_MC_SRV_PREF) is non-zero and the query domain is **.local** a multicast DNS query will be made.

---
### Command Reference:

<a id="AN_CMD_AT_DNS_DNSC"></a>
#### +DNSC

##### Description

This command is used to read or set the DNS configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+DNSC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+DNSC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+DNSC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response             | Description   |
|----------------------|---------------|
| +DNSC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_SVR"></span> 1</p></td>
<td style="text-align: left;"><p>&lt;DNS_SVR&gt;</p></td>
<td style="text-align: left;"><p>IPv4 Address<br />
IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>DNS server IP address<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is 'a.b.c.d'<br />
Format of IPv6 address is 'a:b:c:d::e:f'<br />
This is a multiple value parameter<br />
with an ID range 1.0 to 1.3<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_AUTO"></span> 2</p></td>
<td style="text-align: left;"><p>&lt;DNS_AUTO&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>DNS server auto-assignment<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Manual - use DNS_SVR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Auto - through DHCP etc..</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;DNS_TIMEOUT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>DNS timeout in milliseconds<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_PROTO_PREF"></span> 4</p></td>
<td style="text-align: left;"><p>&lt;DNS_PROTO_PREF&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Result protocol preference<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A preferred over AAAA records.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>AAAA preferred over A records.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>A only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>AAAA only.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_CACHE_TTL"></span> 6</p></td>
<td style="text-align: left;"><p>&lt;DNS_CACHE_TTL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>DNS cache maximum TTL<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>&lt;TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_DNSSEC_MODE"></span> 8</p></td>
<td style="text-align: left;"><p>&lt;DNS_DNSSEC_MODE&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>DNSSEC mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>DNSSEC awareness off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>DNSSEC aware, checking disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>DNSSEC authenticated answers only.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_SRV_PORT"></span> 10</p></td>
<td style="text-align: left;"><p>&lt;DNS_SRV_PORT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>DNS server UDP/TCP port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_SRV_SECURE_PORT"></span> 11</p></td>
<td style="text-align: left;"><p>&lt;DNS_SRV_SECURE_PORT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>DNS server TLS port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_CONN_PREF"></span> 12</p></td>
<td style="text-align: left;"><p>&lt;DNS_CONN_PREF&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Connection preference<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>UDP or TLS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>TCP or TLS.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_MC_SRV_PREF"></span> 13</p></td>
<td style="text-align: left;"><p>&lt;DNS_MC_SRV_PREF&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Multicast server preference<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Not used.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>IPv4 servers only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>IPv6 servers only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>IPv4 &amp; IPv6 servers.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DNSC_STORE_ID_DNS_CONN_IDLE_TIMEOUT"></span> 14</p></td>
<td style="text-align: left;"><p>&lt;DNS_CONN_IDLE_TIMEOUT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>DNS connection idle timeout (in milliseconds)<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_DNS_DNSRESOLV"></a>
#### +DNSRESOLV

##### Description

This command is used to resolve domain names via DNS.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

| Command                              | Description | [Sec](#_security_model) |
|--------------------------------------|-------------|-------------------------|
| AT+DNSRESOLV=\<TYPE\>,\<QUERY_NAME\> | \+          | `GGGG`                  |

**Command Syntax**

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_DNS_DNSRESOLV_TYPE"></span>&lt;TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Type of record<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>NS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>CNAME.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>SOA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>PTR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>MX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>16</p></td>
<td style="text-align: left;"><p>TXT.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>28</p></td>
<td style="text-align: left;"><p>AAAA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>SRV.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>43</p></td>
<td style="text-align: left;"><p>DS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>46</p></td>
<td style="text-align: left;"><p>RRSIG.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>47</p></td>
<td style="text-align: left;"><p>NSEC.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>48</p></td>
<td style="text-align: left;"><p>DNSKEY.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>255</p></td>
<td style="text-align: left;"><p>A+AAAA.</p></td>
</tr>
</tbody>
</table>
<p><br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QUERY_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Query name to resolve<br />
Maximum length of string is 256<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_DNS_DNSRESOLV"></a>
#### +DNSRESOLV

##### Description

**Resolve results.**

| AEC | Description |
|----|----|
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<ADDRESS\> | A & AAAA response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<NSDNAME\> | NS response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<CNAME\> | CNAME response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<MNAME\>,\<SERIAL\>,\<REFRESH\>,\<RETRY\>,\<EXPIRE\>,\<MINIMUM\>,\<RNAME\> | SOA response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<PTRDNAME\> | PTR response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<EXCHANGE\>,\<PREFERENCE\> | MX response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<TXT_DATA\> | TXT response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<TARGET\>,\<PRIORITY\>,\<WEIGHT\>,\<PORT\> | SRV response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<KEY_TAG\>,\<ALGORITHM\>,\<DIGEST_TYPE\>,\<DIGEST\> | DS response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<SIGNER_NAME\>,\<TYPE\>,\<ALGORITHM\>,\<LABELS\>,\<ORIG_TTL\>,\<SIG_EXPIRE\>,\<SIG_INCEPT\>,\<KEY_TAG\>,\<SIGNATURE\> | RRSIG response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<NEXT_DOMAIN\>,\<TYPE_BIT_MAPS\> | NSEC response |
| +DNSRESOLV:\<TYPE\>,\<QUERY_NAME\>,\<FLAGS\>,\<PROTOCOL\>,\<ALGORITHM\>,\<PUBLIC_KEY\> | DNSKEY response |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Type of record<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>NS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>CNAME.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>SOA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>PTR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>MX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>16</p></td>
<td style="text-align: left;"><p>TXT.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>28</p></td>
<td style="text-align: left;"><p>AAAA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>SRV.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>43</p></td>
<td style="text-align: left;"><p>DS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>46</p></td>
<td style="text-align: left;"><p>RRSIG.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>47</p></td>
<td style="text-align: left;"><p>NSEC.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>48</p></td>
<td style="text-align: left;"><p>DNSKEY.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>255</p></td>
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Original query name requested<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>IP address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;NSDNAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Name server domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CNAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Canonical alias domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MNAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Primary name server domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SERIAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Serial number<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;REFRESH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Zone refresh interval<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RETRY&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Zone refresh retry interval<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;EXPIRE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Zone expiry interval<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MINIMUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Minimum exported RR TTL<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RNAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Mailbox domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PTRDNAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Pointer domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;EXCHANGE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Exchange domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PREFERENCE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Preference<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TXT_DATA&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Descriptive text<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TARGET&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Target domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PRIORITY&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Host priority<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;WEIGHT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Relative service weight<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Service port<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY_TAG&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Key tag<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALGORITHM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Algorithm<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DIGEST_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Digest type<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DIGEST&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Digest<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGNER_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Signer’s name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LABELS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of labels<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ORIG_TTL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Original TTL<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIG_EXPIRE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Signature ixpiration<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIG_INCEPT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Signature inception<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGNATURE&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Signature<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;NEXT_DOMAIN&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Next domain name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TYPE_BIT_MAPS&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Type bit maps<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FLAGS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Flags<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Protocol<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>DNSSEC.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PUBLIC_KEY&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Public key<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_DNS_DNSERR"></a>
#### +DNSERR

##### Description

**Resolve failure.**

| AEC                                            | Description     |
|------------------------------------------------|-----------------|
| +DNSERR:\<ERROR_CODE\>,\<TYPE\>,\<QUERY_NAME\> | Resolve failure |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Type of record<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>NS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>CNAME.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>SOA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>PTR.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>MX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>16</p></td>
<td style="text-align: left;"><p>TXT.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>28</p></td>
<td style="text-align: left;"><p>AAAA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>SRV.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>43</p></td>
<td style="text-align: left;"><p>DS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>46</p></td>
<td style="text-align: left;"><p>RRSIG.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>47</p></td>
<td style="text-align: left;"><p>NSEC.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>48</p></td>
<td style="text-align: left;"><p>DNSKEY.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>255</p></td>
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Original query name requested<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

A record query
<a id="EXAMPLE_1a51414e8ba4741b94b30368131eea0cbb47bc44"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=1,"www.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"www.example.com","55.123.145.67"</strong></td>
</tr>
</tbody>
</table>

NS record query
<a id="EXAMPLE_16834ed81435ec93ee5ab05838d2049cfc926893"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=2,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:2,"example.com","ns1.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:2,"example.com","ns2.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"ns1.example.com","192.168.0.1"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:28,"ns1.example.com","1234:5678:ABCD::123"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"ns2.example.com","192.168.0.2"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:28,"ns2.example.com","1234:5678:ABCD::124"</strong></td>
</tr>
</tbody>
</table>

CNAME record query
<a id="EXAMPLE_cee6b3bece566292845ee70ea593b9ac8aba61e9"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=5,"www.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:5,"www.example.com","ano.example.com"</strong></td>
</tr>
</tbody>
</table>

SOA record query
<a id="EXAMPLE_0e97d9dea705e94b6d7a47e08f327b1dbda26c32"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=6,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:6,"example.com","ns1.example.com",1728655446,10800,3600,604800,3600,"admin.example.com"</strong></td>
</tr>
</tbody>
</table>

PTR record query
<a id="EXAMPLE_63f20427cb830943792a52dd0a405d79e485df24"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=12,"67.145.123.55.in-addr.arpa"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:12,"67.145.123.55.in-addr.arpa","www.example.com"</strong></td>
</tr>
</tbody>
</table>

MX record query
<a id="EXAMPLE_cbb40c171c40e12c1958a6d28ccc5ce92c11459e"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=15,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:15,"example.com","mailx.example.com",10</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"mailx.example.com","192.168.0.101"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:28,"mailx.example.com","1234:5678:ABCD::5101"</strong></td>
</tr>
</tbody>
</table>

TXT record query
<a id="EXAMPLE_5cf4dd868566a7d4fdc78b7c53ddcfa7a037d936"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=16,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:16,"example.com","v=spf1 mx a include:_spf.example.com include:_spf.example.com ~all"</strong></td>
</tr>
</tbody>
</table>

AAAA record query
<a id="EXAMPLE_c4b68ffc231410a6beda9e466887b74c3303c800"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=28,"www.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:28,"www.example.com","1234:5678:ABC:D000::EF12"</strong></td>
</tr>
</tbody>
</table>

SRV record query
<a id="EXAMPLE_28e1b5f3b9c1a408085681aa145de2efbbd6e948"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=33,"_imaps._tcp.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:33,"_imaps._tcp.example.com","imap.example.com",5,0,993</strong></td>
</tr>
</tbody>
</table>

DS record query
<a id="EXAMPLE_d2156535c655505f729023b004f3d04d06179bf0"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=43,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:43,"example.com",2371,13,2,\[E44A0F027788…​0BEA77D781\]</strong></td>
</tr>
</tbody>
</table>

NSEC record query
<a id="EXAMPLE_ea72626e881fc800924086c49107f7286274d8d5"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=47,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:47,"example.com","\\000.example.com",\[00096205800C…​01C0\]</strong></td>
</tr>
</tbody>
</table>

DNSKEY record query
<a id="EXAMPLE_28a3cea6a630e35c1ab57bdc97cffb510aa9b719"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=48,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:48,"example.com",257,3,13,\[99DB2CC14CAB…​4BE7778A19\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:48,"example.com",256,3,13,\[A09311112CF9…​806B65E148\]</strong></td>
</tr>
</tbody>
</table>

ANY record query
<a id="EXAMPLE_4bb82ae1e9ae5473ddf7c13902fcf71c771395d2"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=255,"www.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"www.example.com","55.123.145.67"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:28,"www.example.com","1234:5678:ABC:D000::EF12"</strong></td>
</tr>
</tbody>
</table>

A record query With DNSSEC awareness
<a id="EXAMPLE_0f54ad37f94345566cd88df9220d1c69b75d32c3"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSC">+DNSC</a>=8,1</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=1,"www.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"www.example.com","123.45.67.1"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"www.example.com","123.45.67.2"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:46,"www.example.com","example.com",1,13,3,300,1760198187,1760018187,34505,\[D48611C4E419…​48196DD1F7\]</strong></td>
</tr>
</tbody>
</table>

NSEC3PARAM (unknown type) record query
<a id="EXAMPLE_e84478c18562abdd4e2bbc34a253cfb7f08e4f8c"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSC">+DNSC</a>=8,1</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=51,"example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:51,"example.com",\[010000180853…​A4C2\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:46,"example.com","example.com",51,8,2,86400,1761202386,1759992786,43065,\[57BE130BD9BC3E…​9A00B300EC\]</strong></td>
</tr>
</tbody>
</table>

NSEC3 (unknown type) response to invalid A record query
<a id="EXAMPLE_214c64db604a29b4ab723f35f946650640cabcd6"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=1,"0000.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:6,"example.com","ns.example.com",2780200301,1200,180,1209600,60,"techadmin.example.com"</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:46,"example.com","example.com",6,13,2,3600,1760329634,1760066834,56352,\[EB66F399ECCAD5…​FEE205A641\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:46,"11g4e2qvorlg6fqtd14inr597c52fedl.example.com","example.com",50,13,3,60,1760329634,1760066834,56352,\[E90FDC2BDB03…​E5F0A9E1\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:50,"11g4e2qvorlg6fqtd14inr597c52fedl.example.com",\[010000000014…​00000002\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:46,"g5nshuef875ssknoqrrcqg2cait0snsd.example.com","example.com",50,13,3,60,1760329634,1760066834,56352,\[331653EACEF4…​38765448\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:50,"g5nshuef875ssknoqrrcqg2cait0snsd.example.com",\[010000000014…​00000002\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:46,"q0fhrs556u4ps37jqnta5dhrufgu4ths.example.com","example.com",50,13,3,60,1760329634,1760066834,56352,\[AB0CB2CBC0A2…​DDBBAE12\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:50,"q0fhrs556u4ps37jqnta5dhrufgu4ths.example.com",\[010000000014…​00000290\]</strong></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSERR">+DNSERR</a>:5.4,"DNS Non-Existent Domain",1,"0000.example.com"</strong></td>
</tr>
</tbody>
</table>

Multicast A record query
<a id="EXAMPLE_de863d68160befb7fb06d0eb444512ffff122839"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSC">+DNSC</a>=13,3</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=1,"example.local"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"example.local","123.45.6.101"</strong></td>
</tr>
</tbody>
</table>

MDNS-SD of local SSH services
<a id="EXAMPLE_47cd0626aaaf78a7d83763f709beb232b7a5a058"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSC">+DNSC</a>=13,3</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=12,"_ssh._tcp.local"</strong></td>
<td>PTR lookup for _ssh._tcp</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:12,"_ssh._tcp.local","example._ssh._tcp.local"</strong></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=33,"example._ssh._tcp.local"</strong></td>
<td>SRV lookup for example.local SSH service</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:33,"example._ssh._tcp.local","example.local",0,0,22</strong></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=16,"example._ssh._tcp.local"</strong></td>
<td>TXT lookup for example.local SSH service</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:16,"example._ssh._tcp.local",\[\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DNS_DNSRESOLV">+DNSRESOLV</a>=1,"example.local"</strong></td>
<td>A record lookup for example.local</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_DNS_DNSRESOLV">+DNSRESOLV</a>:1,"example.local","123.45.6.101"</strong></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_FS"></a>
## FS (Module ID = 7)

### Command Reference:

<a id="AN_CMD_AT_FS_FLFS_FS"></a>
#### +FS

##### Description

This command performs a filesystem operation.

The filesystem operation command is split into several sub-commands:

- Load

- List

- Delete

- Info

- Store

###### Load Sub-Command:

The load sub-command initiates a file transfer from the DTE to the DCE.

###### List Sub-Command:

The list sub-command produces a list of files present in the filesystem based on the file type specified.

###### Delete Sub-Command:

The delete sub-command deletes a single file object of the type specified from the filesystem.

###### Info Sub-Command:

The info sub-command returns information on the filesystem.

###### Store Sub-Command:

The store sub-command initiates a file transfer from the DCE to the DTE.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+FS=&lt;OP&gt;</p></td>
<td style="text-align: left;"><p>Operate on filesystem<br />
<br />
<a href="#AN_CMD_AT_FS_FLFS_FS_OP">OP</a> must not be 1 or 5</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FS=&lt;OP&gt;,&lt;FILETYPE&gt;</p></td>
<td style="text-align: left;"><p>Operate on file types<br />
<br />
<a href="#AN_CMD_AT_FS_FLFS_FS_OP">OP</a> must not be 1 or 5</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FS=&lt;OP&gt;,&lt;FILETYPE&gt;,&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>Operate on files<br />
<br />
<a href="#AN_CMD_AT_FS_FLFS_FS_OP">OP</a> must not be 1 or 5</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FS=&lt;OP&gt;,&lt;FILETYPE&gt;,&lt;TSFRPROT&gt;,&lt;FILENAME&gt;,&lt;FILELENGTH&gt;</p></td>
<td style="text-align: left;"><p>Load file (single)<br />
<br />
<a href="#AN_CMD_AT_FS_FLFS_FS_OP">OP</a> must be 1</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FS=&lt;OP&gt;,&lt;FILETYPE&gt;,&lt;TSFRPROT&gt;</p></td>
<td style="text-align: left;"><p>Load file (batch)<br />
<br />
<a href="#AN_CMD_AT_FS_FLFS_FS_OP">OP</a> must be 1</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FS=&lt;OP&gt;,&lt;FILETYPE&gt;,&lt;TSFRPROT&gt;,&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>Store file (single)<br />
<br />
<a href="#AN_CMD_AT_FS_FLFS_FS_OP">OP</a> must be 5</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_FS_FLFS_FS_OP"></span>&lt;OP&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Load.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>Store.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILETYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>File type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>The name of the file<br />
Maximum length of string is 32<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TSFRPROT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Transfer protocol<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>X Modem + checksum.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>X Modem + CRC16.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>X Modem 1K.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Y Modem.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>FS-TSFR.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILELENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>File length<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

| Response                                   | Description                    |
|--------------------------------------------|--------------------------------|
| +FS:\<OP\>,\<FILETYPE\>,\<FILENAME\>       | List operation response        |
| +FS:\<OP\>,\<FREE_SPACE\>,\<FREE_HANDLES\> | Information operation response |
| +FS:\<OP\>,\<TSFR_HANDLE\>                 | FS-TSFR response               |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Load.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>Store.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILETYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>File type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>The name of the file<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_SPACE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Free space<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_HANDLES&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Free file handles<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TSFR_HANDLE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Transfer handle<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_FS_FLFS_FSTSFR"></a>
#### +FSTSFR

##### Description

This command performs a filesystem transfer operation.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+FSTSFR</p></td>
<td style="text-align: left;"><p>Transfer query (all)<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FSTSFR=&lt;TSFR_HANDLE&gt;</p></td>
<td style="text-align: left;"><p>Transfer query<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FSTSFR=&lt;TSFR_HANDLE&gt;,&lt;BLOCK_NUM&gt;</p></td>
<td style="text-align: left;"><p>Transfer complete<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FSTSFR=&lt;TSFR_HANDLE&gt;,&lt;BLOCK_NUM&gt;,&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Transfer data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FSTSFR=&lt;TSFR_HANDLE&gt;,&lt;BLOCK_NUM&gt;,&lt;DATA&gt;,&lt;CRC&gt;</p></td>
<td style="text-align: left;"><p>Transfer data (with CRC)<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FSTSFR=&lt;TSFR_HANDLE&gt;,&lt;BLOCK_NUM&gt;</p></td>
<td style="text-align: left;"><p>Store fixed size data, or end<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+FSTSFR=&lt;TSFR_HANDLE&gt;,&lt;BLOCK_NUM&gt;,&lt;DATA_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Store specified data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TSFR_HANDLE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Transfer handle<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BLOCK_NUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Block number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Transfer data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CRC&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Transfer CRC-16<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Data length<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +FSTSFR:\<TSFR_HANDLE\>,\<BLOCK_NUM\>,\<BYTES_REMAIN\> | FS-TSFR load response |
| +FSTSFR:\<TSFR_HANDLE\>,\<BLOCK_NUM\>,\<BYTES_REMAIN\>,\<DATA\> | FS-TSFR store response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Transfer handle<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BLOCK_NUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Block number<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BYTES_REMAIN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Bytes remaining<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Transfer data<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_FS_FLFS_FSUP"></a>
#### +FSUP

##### Description

**Filesystem update.**

| AEC                                                   | Description     |
|-------------------------------------------------------|-----------------|
| +FSUP:\<OP\>,\<FILETYPE\>,\<FILENAME\>,\<FILELENGTH\> | Filesystem load |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Load.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>List.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Delete.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>Store.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILETYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>File type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>The name of the file<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FILELENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
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

File transfer using XModem+CRC with [+FS](#AN_CMD_AT_FS_FLFS_FS)
<a id="EXAMPLE_c3a29205005bd88d52fee5b4c1257e7f8c4851de"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>=1,1,2,"ISRGRootX1",1391</strong></td>
<td>Load 1391 byte certificate using XModem+CRC</td>
</tr>
<tr>
<td>←</td>
<td><code>#</code></td>
<td>Raw binary mode indicator</td>
</tr>
<tr>
<td>←</td>
<td><code>CC</code></td>
<td>Initial handshake, repeating C meaning CRC</td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 01 FE DATA[128] CRC CRC</code></td>
<td>First 128 byte data frame</td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td>Receiver acknowledge</td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 02 FD DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 03 FC DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 04 FB DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 05 FA DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 06 F9 DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 07 F8 DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 08 F7 DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 09 F6 DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 0A F5 DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>SOH 0B F4 DATA[128] CRC CRC</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>EOT</code></td>
<td>End of transmission</td>
</tr>
<tr>
<td>←</td>
<td><code>ACK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><code>OK</code></td>
<td>AT Command completion</td>
</tr>
</tbody>
</table>

List and delete a file
<a id="EXAMPLE_9877579559e5e434da23523503bbceaaebdd6a80"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>=2,1</strong></td>
<td>Request list of certificates</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"AmazonRootCA1"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"BaltimoreCyberTrustRoot"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"DigiCert"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"DigiCertGlobalRootG2"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"DigiCertSHA2"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"EnTrust"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"GlobalSignRoot"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"ISRGRootX1"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"QuoVadis_Root"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,1,"VeriSign"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>=3,1,"AmazonRootCA1"</strong></td>
<td>Delete certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Get filesystem information
<a id="EXAMPLE_2e74f1ef2b6c2ef83ee4e90cb9de68a8a92de661"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>=4</strong></td>
<td>Request filesystem information</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:4,45056,17</strong></td>
<td>45056 bytes, 17 file handles free</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

File load using FS-TSFR protocol
<a id="EXAMPLE_0d368b631cc611ff30c1bc5a3025bc5aee1f7d59"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>=1,1,5,"ExampleCert",891</strong></td>
<td>Load certificate using FS_TSFR</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:1,20489</strong></td>
<td>Certificate transfer handle</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,1,\[308203773082025F…​7420526F6F74301E\]</strong></td>
<td>Send block 1, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,1,763</strong></td>
<td>Ack block 1, 763 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,2,\[170D303030353132…​6F7430820122300D\]</strong></td>
<td>Send block 2, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,2,635</strong></td>
<td>Ack block 2, 635 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,3,\[06092A864886F70D…​C328EAF5AB25878A\]</strong></td>
<td>Send block 3, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,3,507</strong></td>
<td>Ack block 3, 507 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,4,\[9A961CA967B83F0C…​BDC63AECE76E863A\]</strong></td>
<td>Send block 4, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,4,379</strong></td>
<td>Ack block 4, 379 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,5,\[6B97746333BD6818…​010100850C5D8EE4\]</strong></td>
<td>Send block 5, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,5,251</strong></td>
<td>Ack block 5, 251 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,6,\[6F51684205A0DDBB…​A9317A18BFA02AF4\]</strong></td>
<td>Send block 6, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,6,123</strong></td>
<td>Ack block 6, 123 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,7,\[1299F7A34582E33C…​6339A9\]</strong></td>
<td>Send block 7, 123 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,7,0</strong></td>
<td>Ack block 7, no bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

File store using FS-TSFR protocol
<a id="EXAMPLE_a1c1b6e4bee3b5a03437950d9aaa8e7e4cced18f"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>=5,1,5,"ExampleCert"</strong></td>
<td>Store certificate using FS-TSFR</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:5,20489</strong></td>
<td>Certificate transfer handle</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489</strong></td>
<td>Get transfer report</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,0,891</strong></td>
<td>No blocks sent, 891 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,1,128</strong></td>
<td>Receive block 1, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,1,763,\[308203773082025F…​7420526F6F74301E\]</strong></td>
<td>Block 1, 128 bytes, 763 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,2,128</strong></td>
<td>Receive block 2, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,2,635,\[170D303030353132…​6F7430820122300D\]</strong></td>
<td>Block 2, 128 bytes, 635 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,3,128</strong></td>
<td>Receive block 3, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,3,507,\[06092A864886F70D…​C328EAF5AB25878A\]</strong></td>
<td>Block 3, 128 bytes, 507 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,4,128</strong></td>
<td>Receive block 4, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,4,379,\[9A961CA967B83F0C…​BDC63AECE76E863A\]</strong></td>
<td>Block 4, 128 bytes, 379 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,5,128</strong></td>
<td>Receive block 5, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,5,251,\[6B97746333BD6818…​010100850C5D8EE4\]</strong></td>
<td>Block 5, 128 bytes, 251 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,6,128</strong></td>
<td>Receive block 6, 128 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,6,123,\[6F51684205A0DDBB…​A9317A18BFA02AF4\]</strong></td>
<td>Block 6, 128 bytes, 123 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>=20489,7,123</strong></td>
<td>Receive block 7, 123 bytes of data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FSTSFR">+FSTSFR</a>:20489,7,0,\[1299F7A34582E33C5E…​39A9\]</strong></td>
<td>Block 7, 123 bytes, no bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_MQTT"></a>
## MQTT (Module ID = 8)

### Command Reference:

<a id="AN_CMD_AT_MQTT_MQTTC"></a>
#### +MQTTC

##### Description

This command is used to read or set the MQTT configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response              | Description   |
|-----------------------|---------------|
| +MQTTC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;BROKER_ADDR&gt;</p></td>
<td style="text-align: left;"><p>String<br />
IPv4 Address<br />
IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Broker domain name or IP address<br />
Maximum length of string is 256<br />
Format of IPv4 address is 'a.b.c.d'<br />
Format of IPv6 address is 'a:b:c:d::e:f'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;BROKER_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Broker listening TCP port<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;CLIENT_ID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>MQTT client ID<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;USERNAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Username<br />
Maximum length of string is 128<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>&lt;PASSWORD&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Password<br />
Maximum length of string is 256<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>&lt;KEEP_ALIVE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Keep alive time (in seconds)<br />
<br />
Valid range is 0 to 0x7FFF<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>&lt;TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p>
<p>This parameter will only be visible to read if not zero.</p>
<p>Setting a value greater than zero enables TLS and makes this parameter visible.</p>
<p>Setting a value of zero disables TLS and makes this parameter hidden.</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>&lt;PROTO_VER&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>MQTT protocol version, either 3 or 5<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>V3.1.1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>V5.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_MQTTC_STORE_ID_READ_THRESHOLD"></span> 9</p></td>
<td style="text-align: left;"><p>&lt;READ_THRESHOLD&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Subscription read threshold<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;SOCKET_ID&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Socket ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_MQTT_MQTTCONN"></a>
#### +MQTTCONN

##### Description

This command is used to connect to an MQTT broker.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTCONN</p></td>
<td style="text-align: left;"><p>Query current connection status<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTCONN=&lt;CLEAN&gt;</p></td>
<td style="text-align: left;"><p>Start a new connection<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CLEAN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Clean Session<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Use existing session, if available.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Use new session.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_MQTT_MQTTSUB"></a>
#### +MQTTSUB

##### Description

This command is used to subscribe to an MQTT topic.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTSUB=&lt;TOPIC_NAME&gt;,&lt;MAX_QOS&gt;</p></td>
<td style="text-align: left;"><p>Subscribe to a topic<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MAX_QOS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Maximum QoS<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### +MQTTSUBLST

##### Description

This command is used to list MQTT topic subscriptions.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTSUBLST</p></td>
<td style="text-align: left;"><p>List subscriptions<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

| Response                           | Description         |
|------------------------------------|---------------------|
| +MQTTSUBLST:\<TOPIC_NAME\>,\<QOS\> | Subscription report |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QOS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>QoS<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_MQTT_MQTTSUBRD"></a>
#### +MQTTSUBRD

##### Description

This command is used receive data from subscriptions.

The [+MQTTSUBRD](#AN_CMD_AT_MQTT_MQTTSUBRD) command is used in conjunction with the setting of [READ_THRESHOLD](#AN_CMD_MQTTC_STORE_ID_READ_THRESHOLD).

When a message is received the DCE will emit a [+MQTTSUBRX](#AN_AEC_AT_MQTT_MQTTSUBRX) AEC, this will normally include the received data, however when a message is received which would exceed [READ_THRESHOLD](#AN_CMD_MQTTC_STORE_ID_READ_THRESHOLD) the DCE will emit a [+MQTTSUBRX](#AN_AEC_AT_MQTT_MQTTSUBRX) AEC which includes a message ID and data length. This avoids saturating the DTE with data it may not be able to handle. The DTE must use this command to read the buffered message.

Setting [READ_THRESHOLD](#AN_CMD_MQTTC_STORE_ID_READ_THRESHOLD) to zero will cause all received messages to be buffered for reading using this command.

> [!NOTE]
> The message ID is only relevant for QoS1 and QoS2 subscriptions.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTSUBRD=&lt;TOPIC_NAME&gt;,&lt;MSG_ID&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Receive data from a topic<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MSG_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Message Identifier<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes to receive<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +MQTTSUBRD:\<MSG_ID\>,\<MSG_LENGTH\>,\<TOPIC_PAYLOAD\> | Read subscribed data |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Message ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MSG_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length of message<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Payload<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +MQTTUNSUB

##### Description

This command is used to unsubscribe from an MQTT topic.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTUNSUB=&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>Unsubscribe from a topic<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +MQTTPUB

##### Description

This command is used to publish a message.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTPUB=&lt;DUP&gt;,&lt;QOS&gt;,&lt;RETAIN&gt;,&lt;TOPIC_NAME_ID&gt;,&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>Publish to a topic<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;DUP&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Duplicate Message<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>New message.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Duplicate message.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QOS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>QoS<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RETAIN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Retain Message<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Not retained on the server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Retained on the server.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Topic Name or Alias<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Payload<br />
</p></td>
</tr>
</tbody>
</table>

| Response               | Description         |
|------------------------|---------------------|
| +MQTTPUB               | Publish (QoS 0)     |
| +MQTTPUB:\<PACKET_ID\> | Publish (QoS 1 & 2) |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +MQTTLWT

##### Description

This command is used to define a last will message.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTLWT=&lt;QOS&gt;,&lt;RETAIN&gt;,&lt;TOPIC_NAME&gt;,&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>Specific an LWT<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;QOS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>QoS<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RETAIN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Retain Message<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Not retained on the server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Retained on the server.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Payload<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +MQTTDISCONN

##### Description

This command is used to disconnect from a broker.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTDISCONN</p></td>
<td style="text-align: left;"><p>Disconnect<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTDISCONN=&lt;REASON_CODE&gt;</p></td>
<td style="text-align: left;"><p>Disconnect with a reason<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;REASON_CODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Reason Code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Normal disconnection.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Disconnect with Will Message.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>128</p></td>
<td style="text-align: left;"><p>Unspecified error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>129</p></td>
<td style="text-align: left;"><p>Malformed packet.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>130</p></td>
<td style="text-align: left;"><p>Protocol error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>131</p></td>
<td style="text-align: left;"><p>Implementation specific error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>144</p></td>
<td style="text-align: left;"><p>Topic name invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>147</p></td>
<td style="text-align: left;"><p>Receive maximum exceeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>148</p></td>
<td style="text-align: left;"><p>Topic alias invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>149</p></td>
<td style="text-align: left;"><p>Packet too large.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>150</p></td>
<td style="text-align: left;"><p>Message rate too high.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>151</p></td>
<td style="text-align: left;"><p>Quota exceeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>152</p></td>
<td style="text-align: left;"><p>Administrative action.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>153</p></td>
<td style="text-align: left;"><p>Payload format invalid.</p></td>
</tr>
</tbody>
</table>
<p><br />
Unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +MQTTPROPTX

##### Description

This command is used to read or set the MQTT transmit properties.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

Any defined and selected properties are added to transmitted MQTT packets. Only properties applicable to the MQTT packet type are added. Properties must be selected via the [+MQTTPROPTXS](#AN_CMD_AT_MQTT_MQTTPROPTXS) command before they are included.

> [!NOTE]
> Not all properties listed below may be available in any implementation of this command set.

User property (38) supports multiple entries in the form of key/value pairs. If a key/value pair is specified for the command it will be added, if only a key is specified it will be removed.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTX</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTX=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTX=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
<br />
<a href="#AN_CMD_AT_MQTT_MQTTPROPTX_ID">ID</a> must not be 38</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTX=&lt;ID&gt;,&lt;KEY&gt;,&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>Set a single key/value pair<br />
<br />
<a href="#AN_CMD_AT_MQTT_MQTTPROPTX_ID">ID</a> must be 38</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTX=&lt;ID&gt;,&lt;KEY&gt;</p></td>
<td style="text-align: left;"><p>Clear a single key/value pair<br />
<br />
<a href="#AN_CMD_AT_MQTT_MQTTPROPTX_ID">ID</a> must be 38</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_MQTT_MQTTPROPTX_ID"></span>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;KEY&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response                            | Description               |
|-------------------------------------|---------------------------|
| +MQTTPROPTX:\<ID\>,\<VAL\>          | Read response             |
| +MQTTPROPTX:\<ID\>,\<KEY\>,\<VALS\> | Read response (key/value) |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;PAYLOAD_FORMAT_IND&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Payload Format Indicator<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;MSG_EXPIRY_INTERVAL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Message Expiry Interval<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;CONTENT_TYPE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Content Type<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>&lt;RESP_TOPIC&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Response Topic<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>&lt;CORRELATION_DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Correlation Data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>&lt;SUBSCRIPTION_ID&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Subscription Identifier<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>17</p></td>
<td style="text-align: left;"><p>&lt;SESSION_EXPIRY_INTERVAL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Session Expiry Interval<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>23</p></td>
<td style="text-align: left;"><p>&lt;REQ_PROB_INFO&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Request Problem Information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>24</p></td>
<td style="text-align: left;"><p>&lt;WILL_DELAY_INTERVAL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Will Delay Interval<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>25</p></td>
<td style="text-align: left;"><p>&lt;REQ_RESP_INFO&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Request Response Information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>&lt;REASON_STR&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Reason String<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>&lt;RECEIVE_MAX&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Receive Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>&lt;TOPIC_ALIAS_MAX&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Topic Alias Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>35</p></td>
<td style="text-align: left;"><p>&lt;TOPIC_ALIAS&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Topic Alias<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>38</p></td>
<td style="text-align: left;"><p>&lt;USER_PROP&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>User Property<br />
This is a multiple value parameter<br />
with an ID range 38.0 to 38.9<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>39</p></td>
<td style="text-align: left;"><p>&lt;MAX_PACKET_SZ&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Maximum Packet Size<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
#### +MQTTPROPRX

##### Description

This command is used to read or reset the MQTT receive properties.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

Any defined properties are added to transmitted MQTT packets. Only properties applicable to the MQTT packet type are added.

Any properties received are added to the list of available receive properties which can be queried by this command. Updates to the received properties are announced using the [+MQTTPROPRX](#AN_AEC_AT_MQTT_MQTTPROPRX) AEC and can be read via this command.

> [!NOTE]
> Not all properties listed below may be available in any implementation of this command set.

User property (38) supports multiple entries in the form of key/value pairs.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPRX</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPRX=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPRX=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
<br />
<a href="#AN_CMD_AT_MQTT_MQTTPROPRX_ID">ID</a> must be 0</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_MQTT_MQTTPROPRX_ID"></span>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response                            | Description               |
|-------------------------------------|---------------------------|
| +MQTTPROPRX:\<ID\>,\<VAL\>          | Read response             |
| +MQTTPROPRX:\<ID\>,\<KEY\>,\<VALS\> | Read response (key/value) |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;PAYLOAD_FORMAT_IND&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Payload Format Indicator<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;MSG_EXPIRY_INTERVAL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Message Expiry Interval<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;CONTENT_TYPE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Content Type<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>&lt;RESP_TOPIC&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Response Topic<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>&lt;CORRELATION_DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Correlation Data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>&lt;SUBSCRIPTION_ID&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Subscription Identifier<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>17</p></td>
<td style="text-align: left;"><p>&lt;SESSION_EXPIRY_INTERVAL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Session Expiry Interval<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>18</p></td>
<td style="text-align: left;"><p>&lt;ASSIGNED_CLIENT_ID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Assigned Client Identifier<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>19</p></td>
<td style="text-align: left;"><p>&lt;SERVER_KEEP_ALIVE&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Server Keep Alive<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>23</p></td>
<td style="text-align: left;"><p>&lt;REQ_PROB_INFO&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Request Problem Information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>25</p></td>
<td style="text-align: left;"><p>&lt;REQ_RESP_INFO&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Request Response Information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>26</p></td>
<td style="text-align: left;"><p>&lt;RESP_INFO&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Response Information<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>28</p></td>
<td style="text-align: left;"><p>&lt;SERVER_REF&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Server Reference<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>&lt;REASON_STR&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Reason String<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>&lt;RECEIVE_MAX&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Receive Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>&lt;TOPIC_ALIAS_MAX&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Topic Alias Maximum<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>35</p></td>
<td style="text-align: left;"><p>&lt;TOPIC_ALIAS&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Topic Alias<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>36</p></td>
<td style="text-align: left;"><p>&lt;MAX_QOS&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Maximum QoS<br />
<br />
Valid range is 0 to 2<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>37</p></td>
<td style="text-align: left;"><p>&lt;RETAIN_AVAIL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Retain Available<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>38</p></td>
<td style="text-align: left;"><p>&lt;USER_PROP&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>User Property<br />
This is a multiple value parameter<br />
with an ID range 38.0 to 38.9<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>39</p></td>
<td style="text-align: left;"><p>&lt;MAX_PACKET_SZ&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Maximum Packet Size<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>&lt;WILDCARD_SUB_AVAIL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Wildcard Subscription Available<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>41</p></td>
<td style="text-align: left;"><p>&lt;SUBSCRIPTION_ID_AVAIL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Subscription Identifier Available<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>42</p></td>
<td style="text-align: left;"><p>&lt;SHARED_SUBSCRIPTION_AVAIL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Shared Subscription Available<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_MQTT_MQTTPROPTXS"></a>
#### +MQTTPROPTXS

##### Description

This command is used to define which transmit properties are selected.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTXS</p></td>
<td style="text-align: left;"><p>Query all IDs<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTXS=&lt;PROP_ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+MQTTPROPTXS=&lt;PROP_ID&gt;,&lt;PROP_SEL&gt;</p></td>
<td style="text-align: left;"><p>Set a single ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PROP_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Property Identifier<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>All properties.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Payload Format Indicator.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Message Expiry Interval.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Content Type.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>Response Topic.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>Correlation Data.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>Subscription Identifier.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>17</p></td>
<td style="text-align: left;"><p>Session Expiry Interval.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>23</p></td>
<td style="text-align: left;"><p>Request Problem Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>24</p></td>
<td style="text-align: left;"><p>Will Delay Interval.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>25</p></td>
<td style="text-align: left;"><p>Request Response Information.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>Reason String.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>Receive Maximum.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>Topic Alias Maximum.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>35</p></td>
<td style="text-align: left;"><p>Topic Alias.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>38</p></td>
<td style="text-align: left;"><p>User Property.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>39</p></td>
<td style="text-align: left;"><p>Maximum Packet Size.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROP_SEL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Property Selected<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Property not selected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Property is selected.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response                              | Description   |
|---------------------------------------|---------------|
| +MQTTPROPTXS:\<PROP_ID\>,\<PROP_SEL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Property Identifier<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROP_SEL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Property Selected<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Property not selected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Property is selected.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_MQTT_MQTTCONN"></a>
#### +MQTTCONN

##### Description

**Connection state.**

| AEC                      | Description      |
|--------------------------|------------------|
| +MQTTCONN:\<CONN_STATE\> | Connection state |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>MQTT connected state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Not connected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Connected.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_MQTT_MQTTCONNACK"></a>
#### +MQTTCONNACK

##### Description

**Connection acknowledge.**

| AEC                                                 | Description      |
|-----------------------------------------------------|------------------|
| +MQTTCONNACK:\<CONNACK_FLAGS\>,\<CONN_REASON_CODE\> | Connection state |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Connect acknowledge flags<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>No session.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Session present.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CONN_REASON_CODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Connect reason code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Success.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>128</p></td>
<td style="text-align: left;"><p>Unspecified error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>129</p></td>
<td style="text-align: left;"><p>Malformed packet.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>130</p></td>
<td style="text-align: left;"><p>Protocol error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>131</p></td>
<td style="text-align: left;"><p>Implementation specific error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>132</p></td>
<td style="text-align: left;"><p>Unsupported protocol version.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>133</p></td>
<td style="text-align: left;"><p>Client identifier not valid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>134</p></td>
<td style="text-align: left;"><p>Bad username or password.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>135</p></td>
<td style="text-align: left;"><p>Not authorized.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>136</p></td>
<td style="text-align: left;"><p>Server unavailable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>137</p></td>
<td style="text-align: left;"><p>Server busy.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>138</p></td>
<td style="text-align: left;"><p>Banned.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>140</p></td>
<td style="text-align: left;"><p>Bad authentication method.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>144</p></td>
<td style="text-align: left;"><p>Topic name invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>149</p></td>
<td style="text-align: left;"><p>Packet too large.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>151</p></td>
<td style="text-align: left;"><p>Quota exceeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>153</p></td>
<td style="text-align: left;"><p>Payload format invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>154</p></td>
<td style="text-align: left;"><p>Retain not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>155</p></td>
<td style="text-align: left;"><p>QoS not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>156</p></td>
<td style="text-align: left;"><p>Use another server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>156</p></td>
<td style="text-align: left;"><p>Server moved.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>159</p></td>
<td style="text-align: left;"><p>Connection rate exceeded.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### +MQTTPUBACK

##### Description

**Publish acknowledge.**

| AEC                       | Description         |
|---------------------------|---------------------|
| +MQTTPUBACK:\<PACKET_ID\> | Publish acknowledge |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +MQTTPUBCOMP

##### Description

**Publish complete.**

| AEC                        | Description      |
|----------------------------|------------------|
| +MQTTPUBCOMP:\<PACKET_ID\> | Publish complete |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +MQTTPUBERR

##### Description

**Publish error.**

| AEC                       | Description   |
|---------------------------|---------------|
| +MQTTPUBERR:\<PACKET_ID\> | Publish error |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Packet ID<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_MQTT_MQTTSUB"></a>
#### +MQTTSUB

##### Description

**Subscribe response.**

| AEC                      | Description        |
|--------------------------|--------------------|
| +MQTTSUB:\<REASON_CODE\> | Subscribe response |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>SUBACK return code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Granted QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Granted QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Granted QoS 2.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>128</p></td>
<td style="text-align: left;"><p>Unspecified error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>131</p></td>
<td style="text-align: left;"><p>Implementation specific error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>135</p></td>
<td style="text-align: left;"><p>Not authorized.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>143</p></td>
<td style="text-align: left;"><p>Topic filter invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>145</p></td>
<td style="text-align: left;"><p>Packet identifier in use.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>151</p></td>
<td style="text-align: left;"><p>Quota exceeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>158</p></td>
<td style="text-align: left;"><p>Shared Subscriptions not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>161</p></td>
<td style="text-align: left;"><p>Subscription identifiers not supported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>162</p></td>
<td style="text-align: left;"><p>Wildcard subscriptions not supported.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### +MQTTUNSUB

##### Description

**Unsubscribe response.**

| AEC                   | Description          |
|-----------------------|----------------------|
| +MQTTUNSUB:\<RESULT\> | Unsubscribe response |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Result of unsubscribe request<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Success.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>15</p></td>
<td style="text-align: left;"><p>No subscription existed.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>128</p></td>
<td style="text-align: left;"><p>Unspecified error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>131</p></td>
<td style="text-align: left;"><p>Implementation specific error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>135</p></td>
<td style="text-align: left;"><p>Not authorized.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>143</p></td>
<td style="text-align: left;"><p>Topic filter invalid.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>145</p></td>
<td style="text-align: left;"><p>Packet identifier in use.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_MQTT_MQTTSUBRX"></a>
#### +MQTTSUBRX

##### Description

**Receive subscribed data.**

| AEC | Description |
|----|----|
| +MQTTSUBRX:\<DUP\>,\<QOS\>,\<RETAIN\>,\<TOPIC_NAME\>,\<TOPIC_PAYLOAD\> | Received subscribed data |
| +MQTTSUBRX:\<DUP\>,\<QOS\>,\<RETAIN\>,\<TOPIC_NAME\>,\<MSG_ID\>,\<MSG_LENGTH\> | Received subscribed data notification |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Duplicate Message<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>New message.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Duplicate message.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;QOS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>QoS<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>QoS 0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>QoS 1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>QoS 2.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RETAIN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Retain Message<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Not retained on the server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Retained on the server.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TOPIC_PAYLOAD&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Topic Payload<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MSG_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Message ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MSG_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length of message<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_MQTT_MQTTPROPRX"></a>
#### +MQTTPROPRX

##### Description

**Indicates property has been updated.**

| AEC | Description |
|----|----|
| +MQTTPROPRX:\<PROP_ID\> | Property ID updated |
| +MQTTPROPRX:\<PROP_ID\>,\<VAL\> | Property ID updated, with value |
| +MQTTPROPRX:\<PROP_ID\>,\<KEY\>,\<VALS\> | Property ID updated, with key/value pair |

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
<td style="text-align: left;"><p>Integer<br />
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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter key<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

MQTT connection directly over TLS
<a id="EXAMPLE_763df688af86d232581b5749c292a4aadffbdcd4"></a>

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_TIME_TIME">+TIME</a>:3969510079</strong></td>
<td>Wait for time for correct TLS operation</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,1,"ServerCACert"</strong></td>
<td>Set the broker CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,6,"example.com"</strong></td>
<td>Set the broker domain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=1,"mqtt.example.com"</strong></td>
<td>Set the broker hostname</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=2,8883</strong></td>
<td>Set the MQTTS port number</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=3,"clientid"</strong></td>
<td>Set client ID</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=4,"username"</strong></td>
<td>Set username</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=5,"password"</strong></td>
<td>Set password</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=7,1</strong></td>
<td>Use TLSC index 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTCONN">+MQTTCONN</a>=1</strong></td>
<td>Connect to broker</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:34,10</strong></td>
<td>Received property Topic Alias Max=10</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:33,20</strong></td>
<td>Received property Receive Max=20</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTCONNACK">+MQTTCONNACK</a>:0,0</strong></td>
<td>CONNACK response</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTCONN">+MQTTCONN</a>:1</strong></td>
<td>Connected</td>
</tr>
</tbody>
</table>

MQTT connection over TLS socket
<a id="EXAMPLE_8cb9b789fe72ee96a4f00e56c7528fefed94d312"></a>

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_TIME_TIME">+TIME</a>:3969510551</strong></td>
<td>Wait for time for correct TLS operation</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>=2</strong></td>
<td>Open TCP socket</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>:17604</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,1,"ServerCACert"</strong></td>
<td>Set the broker CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,6,"example.com"</strong></td>
<td>Set the broker domain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=3,"clientid"</strong></td>
<td>Set client ID</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=4,"username"</strong></td>
<td>Set username</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=5,"password"</strong></td>
<td>Set password</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=10,17604</strong></td>
<td>Assign socket ID to MQTT configuration</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKTLS">+SOCKTLS</a>=17604,1</strong></td>
<td>Upgrade socket to TLS</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKBR">+SOCKBR</a>=17604,"mqtt.example.com",8883</strong></td>
<td>Bind socket to server</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKIND">+SOCKIND</a>:17604,"1.2.3.4",65333,"5.6.7.8",8883</strong></td>
<td>Socket connected</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKTLS">+SOCKTLS</a>:17604</strong></td>
<td>Socket upgraded to TLS</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTCONN">+MQTTCONN</a>=1</strong></td>
<td>Connect to broker</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:34,10</strong></td>
<td>Received property Topic Alias Max=10</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:33,20</strong></td>
<td>Received property Receive Max=20</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTCONNACK">+MQTTCONNACK</a>:0,0</strong></td>
<td>CONNACK response</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTCONN">+MQTTCONN</a>:1</strong></td>
<td>Connected</td>
</tr>
</tbody>
</table>

Subscribe to MQTT topic and receive data (asynchronously)
<a id="EXAMPLE_520a41f5f278cbdca5ec88603f0abace550e4c65"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTSUB">+MQTTSUB</a>="Topic/name",1</strong></td>
<td>Subscribe to topic with QoS=1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTSUB">+MQTTSUB</a>:1</strong></td>
<td>Subscription granted QoS=1</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:1,0</strong></td>
<td>Message property 1 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:3,"text/plain"</strong></td>
<td>Message property 3 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTSUBRX">+MQTTSUBRX</a>:0,1,0,"Topic/name","ExampleText1"</strong></td>
<td>Message received with data</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:1,0</strong></td>
<td>Message property 1 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:3,"text/plain"</strong></td>
<td>Message property 3 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTSUBRX">+MQTTSUBRX</a>:0,1,0,"Topic/name","ExampleText2"</strong></td>
<td>Message received with data</td>
</tr>
</tbody>
</table>

Subscribe to MQTT topic and receive data (polled)
<a id="EXAMPLE_e86e402f305e460d8856aba5d60360834676ed35"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTSUB">+MQTTSUB</a>="Topic/name",1</strong></td>
<td>Subscribe to topic with QoS=1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTSUB">+MQTTSUB</a>:1</strong></td>
<td>Subscription granted QoS=1</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTC">+MQTTC</a>=9,0</strong></td>
<td>Configure receive threshold to zero bytes</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:1,0</strong></td>
<td>Message property 1 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:3,"text/plain"</strong></td>
<td>Message property 3 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTSUBRX">+MQTTSUBRX</a>:0,1,0,"Topic/name",1,12</strong></td>
<td>Message received, ID=1, length=12</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:1,0</strong></td>
<td>Message property 1 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTPROPRX">+MQTTPROPRX</a>:3,"text/plain"</strong></td>
<td>Message property 3 received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_MQTT_MQTTSUBRX">+MQTTSUBRX</a>:0,1,0,"Topic/name",2,12</strong></td>
<td>Message received, ID=2, length=12</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTSUBRD">+MQTTSUBRD</a>="Topic/name",1,12</strong></td>
<td>Read message ID=1</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_MQTT_MQTTSUBRD">+MQTTSUBRD</a>:11,"ExampleText1"</strong></td>
<td>Message ID=1 data</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_MQTT_MQTTSUBRD">+MQTTSUBRD</a>="Topic/name",2,12</strong></td>
<td>Read message ID=2</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_MQTT_MQTTSUBRD">+MQTTSUBRD</a>:11,"ExampleText2"</strong></td>
<td>Message ID=2 data</td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_NETIF"></a>
## NETIF (Module ID = 9)

### Command Reference:

<a id="AN_CMD_AT_NETIF_NETIFC"></a>
#### +NETIFC

##### Description

This command is used to read or set the network interface configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+NETIFC</p></td>
<td style="text-align: left;"><p>Query interface list<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+NETIFC=&lt;INTF&gt;</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+NETIFC=&lt;INTF&gt;,&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+NETIFC=&lt;INTF&gt;,&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;INTF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Interface number<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response                  | Description   |
|---------------------------|---------------|
| +NETIFC:\<INTF\>,\<INTF\> | List response |
| +NETIFC:\<ID\>,\<VAL\>    | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Interface number<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Network interface name<br />
Maximum length of string is 16<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;ETHER&gt;</p></td>
<td style="text-align: left;"><p>MAC Address<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Ethernet MAC address of interface<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;HOSTNAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Name of this interface<br />
Maximum length of string is 16<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;DHCPC_EN&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>DHCP client enable<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disabled - use static configuration.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enabled - use automatic settings.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>&lt;DHCPC_LEASE_START&gt;</p></td>
<td style="text-align: left;"><p>UTC Time<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>DHCP lease start time, displayed in system time format<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>&lt;DHCPC_LEASE_ENDS&gt;</p></td>
<td style="text-align: left;"><p>UTC Time<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>DHCP lease end time, displayed in system time format<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>&lt;DHCPC_SRV_ADDR&gt;</p></td>
<td style="text-align: left;"><p>IPv4 Address<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>IP address of DHCP server<br />
<br />
Unsigned 32-bit value<br />
Format of IPv4 address is 'a.b.c.d'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>&lt;L2_ONLY&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Layer 2 only flag<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Layer 3 active.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Layer 3 not active.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>&lt;L2_MONITOR_MODE&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>L2 monitor mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Unicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Broadcast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Unicast + Broadcast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Multicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>Unicast + Multicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>Broadcast + Multicast.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>Unicast + Broadcast + Multicast.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>&lt;L2_MONITOR_MAX_LEN&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>L2 monitor max length<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>&lt;IP_MASK&gt;</p></td>
<td style="text-align: left;"><p>IPv4 Address<br />
</p></td>
<td style="text-align: left;"><p>IP address and net mask<br />
Format of IPv4 address is 'a.b.c.d/m'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>41</p></td>
<td style="text-align: left;"><p>&lt;GATEWAY&gt;</p></td>
<td style="text-align: left;"><p>IPv4 Address<br />
</p></td>
<td style="text-align: left;"><p>IP address of gateway<br />
Format of IPv4 address is 'a.b.c.d'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>60</p></td>
<td style="text-align: left;"><p>&lt;IPV6_GLO_ADDR&gt;</p></td>
<td style="text-align: left;"><p>IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>IPv6 global address<br />
Format of IPv6 address is 'a:b:c:d::e:f/m'<br />
This is a multiple value parameter<br />
with an ID range 60.0 to 60.1<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>61</p></td>
<td style="text-align: left;"><p>&lt;IPV6_LL_ADDR&gt;</p></td>
<td style="text-align: left;"><p>IPv6 Address<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>IPv6 link-local address<br />
Format of IPv6 address is 'a:b:c:d::e:f/m'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>62</p></td>
<td style="text-align: left;"><p>&lt;IPV6_GATEWAY&gt;</p></td>
<td style="text-align: left;"><p>IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>IPv6 gateway address<br />
Format of IPv6 address is 'a:b:c:d::e:f'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
#### +NETIFTX

##### Description

This command is used to send L2 data frames.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+NETIFTX=&lt;INTF&gt;,&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Send an L2 data frame<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;INTF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Interface number<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Data frame data<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +NETIFRX

##### Description

**Received L2 data frame.**

| AEC                                        | Description   |
|--------------------------------------------|---------------|
| +NETIFRX:\<INTF\>,\<DATA_LENGTH\>,\<DATA\> | L2 data frame |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Interface number<br />
<br />
Valid range is 0 to 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Data frame<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_OTA"></a>
## OTA (Module ID = 10)

### Introduction

Over-the-air (OTA) allows the firmware of the DCE to be upgraded. There are two OTA methods: an internal HTTP/HTTPS download based method using [OTA (Module ID = 10)](#AN_MOD_OTA) commands; or a host controlled flash write based method using [NVM (Module ID = 29)](#AN_MOD_NVM) commands.

Both methods make use of an alternate firmware image partition in non-volatile memory. The new image is placed in the alternate partition, then verified and activated. Once the new image has been activated, the current image continues to run, but the new image will have higher priority to run at the next boot.

After a successful OTA, activation and reboot, the alternate firmware image partition will contain the previously run image. It is possible to rollback to this previous image using the [+OTAINV](#AN_CMD_AT_OTA_OTAINV) command. This command verifies the previous image, then invalidates the current running firmware image, so that it cannot be booted again. The current image continues to run, but the previous image will run at the next boot.

> [!NOTE]
> If the OTA feature is not being utilised, the alternate firmware image partition on the DCE can be used for data storage. The partition supports up to 960kB of data. Data can be erased, written, read and checked via the NVM commands.

#### Timeout

A timeout is set for the internal OTA, if a data packet is not received within *n* seconds or *n* second gap occurs between packets, then the OTA process will be stopped. The default timeout is 20 seconds.

> [!NOTE]
> It may be necessary to use a timeout greater than the default if the network conditions are poor, or the server has a high latency.

#### Troubleshooting

Further firmware image information can be gathered with the [+DI](#AN_CMD_AT_DI_DI) command which can help with debugging available images on the DCE.

#### Internal HTTP/S OTA Example

For OTA using the internal HTTP/HTTPS download based method, a HTTP server is required to serve the firmware image file. The DTE configures the download, then downloads and activates the new image. Image verification is done internally when the download completes.

##### HTTP Configuration

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=2,"example.com"</strong></td>
<td>Set host</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=3,80</strong></td>
<td>Set port</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=4,"/firmware/"</strong></td>
<td>Set path</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=5,"rnwf02_ota.bootable.bin"</strong></td>
<td>Set filename</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

##### HTTPS Configuration

**To use HTTPS a TLS configuration is required.**

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=7,1</strong></td>
<td>Set TLS configuration</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

##### Download and Activation

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTADL">+OTADL</a>=1</strong></td>
<td>Request OTA download</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTADL">+OTADL</a>:1</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.0,"Erase Done"</strong></td>
<td>Partiton erased AEC</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.1,"Write Done"</strong></td>
<td>Firmware image written AEC</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.2,"Verify Done"</strong></td>
<td>Firmware image verified AEC</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a></strong></td>
<td>Request to activate firmware</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a>:2</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:2,10.3,"Activate Done"</strong></td>
<td>Activation successful AEC</td>
</tr>
</tbody>
</table>

#### NVM OTA Example

For OTA using the host controlled flash write based method, the DTE accesses the alternate firmware image partition of the DCE with flash read/write/erase commands. This feature allows extra flexibility with the data transport method, and ability to implement more advanced OTA logic if required - such as piecemeal updating with persistence between power cycles.

Once the DTE has written the image to the DCE using [NVM (Module ID = 29)](#AN_MOD_NVM) commands, the DTE should verify and activate the new image using [OTA (Module ID = 10)](#AN_MOD_OTA) commands.

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMWR">+NVMWR</a>=0,512,\[FFFFFFFF0101E0005048434D0300000000000300FFFFFFFF…​\]</strong></td>
<td>Write firmware image data</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMWR">+NVMWR</a>=0,512,\[…​\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td></td>
<td><code>…​</code></td>
<td>Continue until writing finished</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAVFY">+OTAVFY</a></strong></td>
<td>Request to verify firmware image</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTAVFY">+OTAVFY</a>:1</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.2,"Verify Done"</strong></td>
<td>Firmware image verified AEC</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a></strong></td>
<td>Request to activate firmware</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a>:2</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:2,10.3,"Activate Done"</strong></td>
<td>Activation successful AEC</td>
</tr>
</tbody>
</table>

---
### Command Reference:

<a id="AN_CMD_AT_OTA_OTAC"></a>
#### +OTAC

##### Description

This command is used to read or set the OTA configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+OTAC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+OTAC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+OTAC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Protocol type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>HTTP.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;HOST&gt;</p></td>
<td style="text-align: left;"><p>String<br />
IPv4 Address<br />
IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Host domain name or IP address<br />
Maximum length of string is 255<br />
Format of IPv4 address is 'a.b.c.d'<br />
Format of IPv6 address is 'a:b:c:d::e:f'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;PORT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Listening port<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;PATH&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Path to firmware<br />
Maximum length of string is 1024<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>&lt;FILE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Firmware file<br />
Maximum length of string is 1024<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>&lt;TIMEOUT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Timeout in seconds<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>&lt;TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;SOCKET_ID&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Socket ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_OTA_OTADL"></a>
#### +OTADL

##### Description

This command allows the downloading of firmware to the DCE.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+OTADL=&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Download OTA image<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Enable the OTA download feature<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Use configuration from +OTAC command.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response             | Description           |
|----------------------|-----------------------|
| +OTADL:\<OTA_OP_ID\> | OTA download response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_OTA_OTAVFY"></a>
#### +OTAVFY

##### Description

This command verifies the OTA firmware image.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+OTAVFY</p></td>
<td style="text-align: left;"><p>Verify OTA image<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

| Response              | Description         |
|-----------------------|---------------------|
| +OTAVFY:\<OTA_OP_ID\> | OTA verify response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_OTA_OTAACT"></a>
#### +OTAACT

##### Description

This command activates the OTA firmware image.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+OTAACT</p></td>
<td style="text-align: left;"><p>Activate OTA image<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

| Response              | Description           |
|-----------------------|-----------------------|
| +OTAACT:\<OTA_OP_ID\> | OTA activate response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_OTA_OTAINV"></a>
#### +OTAINV

##### Description

This command will invalidate the current running firmware image. Invalidation does not delete the current running firmware image.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+OTAINV</p></td>
<td style="text-align: left;"><p>Invalidate current running image<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

| Response              | Description             |
|-----------------------|-------------------------|
| +OTAINV:\<OTA_OP_ID\> | OTA invalidate response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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

<a id="AN_AEC_AT_OTA_OTA"></a>
#### +OTA

##### Description

**OTA state.**

| AEC                              | Description |
|----------------------------------|-------------|
| +OTA:\<OTA_OP_ID\>,\<OTA_STATE\> | OTA status  |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OTA_STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Status code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Erase done.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Write done.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Verify done.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Activate done.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
#### +OTAERR

##### Description

**OTA error.**

| AEC                                  | Description |
|--------------------------------------|-------------|
| +OTAERR:\<OTA_OP_ID\>,\<ERROR_CODE\> | OTA error   |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation ID<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

Internal OTA HTTP Configuration
<a id="EXAMPLE_OTA_HTTP_CONF"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=2,"example.com"</strong></td>
<td>Set host</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=3,80</strong></td>
<td>Set port</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=4,"/firmware/"</strong></td>
<td>Set path</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=5,"rnwf02_ota.bootable.bin"</strong></td>
<td>Set filename</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Internal OTA HTTPS Configuration
<a id="EXAMPLE_OTA_HTTPS_CONF"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAC">+OTAC</a>=7,1</strong></td>
<td>Set TLS configuration</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Internal OTA
<a id="EXAMPLE_OTA_INTERNAL"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTADL">+OTADL</a>=1</strong></td>
<td>Request OTA download</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTADL">+OTADL</a>:1</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.0,"Erase Done"</strong></td>
<td>Partiton erased AEC</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.1,"Write Done"</strong></td>
<td>Firmware image written AEC</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.2,"Verify Done"</strong></td>
<td>Firmware image verified AEC</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a></strong></td>
<td>Request to activate firmware</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a>:2</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:2,10.3,"Activate Done"</strong></td>
<td>Activation successful AEC</td>
</tr>
</tbody>
</table>

NVM OTA
<a id="EXAMPLE_OTA_NVM"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMWR">+NVMWR</a>=0,512,\[FFFFFFFF0101E0005048434D0300000000000300FFFFFFFF…​\]</strong></td>
<td>Write firmware image data</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMWR">+NVMWR</a>=0,512,\[…​\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td></td>
<td><code>…​</code></td>
<td>Continue until writing finished</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAVFY">+OTAVFY</a></strong></td>
<td>Request to verify firmware image</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTAVFY">+OTAVFY</a>:1</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:1,10.2,"Verify Done"</strong></td>
<td>Firmware image verified AEC</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a></strong></td>
<td>Request to activate firmware</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_OTA_OTAACT">+OTAACT</a>:2</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_OTA_OTA">+OTA</a>:2,10.3,"Activate Done"</strong></td>
<td>Activation successful AEC</td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_PING"></a>
## PING (Module ID = 11)

### Command Reference:

#### +PING

##### Description

This command sends a ping (ICMP Echo Request) to the target address.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+PING=&lt;TARGET_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Ping a target address<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+PING=&lt;TARGET_ADDR&gt;,&lt;PROTOCOL_VERSION&gt;</p></td>
<td style="text-align: left;"><p>Ping a target address (specifying IP protocol)<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;TARGET_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>IP address or host name of target<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROTOCOL_VERSION&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>IP protocol version<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>IPv4.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>IPv6.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +PING

##### Description

**Successful ping.**

| AEC                          | Description           |
|------------------------------|-----------------------|
| +PING:\<IP_ADDRESS\>,\<RTT\> | Ping success response |

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
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>IP address of the target<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RTT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Round trip time (in milliseconds)<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +PINGERR

##### Description

**Error.**

| AEC                     | Description |
|-------------------------|-------------|
| +PINGERR:\<ERROR_CODE\> | Ping error  |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
## RST (Module ID = 12)

### Command Reference:

#### +RST

##### Description

This command is used to reset the DCE.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+RST</p></td>
<td style="text-align: left;"><p>Reset target<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
---
<a id="AN_MOD_SNTP"></a>
## SNTP (Module ID = 13)

### Command Reference:

#### +SNTPC

##### Description

This command is used to read or set the SNTP configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SNTPC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SNTPC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SNTPC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response              | Description   |
|-----------------------|---------------|
| +SNTPC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;NTP_ENABLED&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Network Time (NTP) client function<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;NTP_STATIC&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>NTP configuration mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Auto-assigned by network.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Manually configured by user.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;NTP_SVR&gt;</p></td>
<td style="text-align: left;"><p>String<br />
IPv4 Address<br />
IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>The address/name of NTP server<br />
Maximum length of string is 128<br />
Format of IPv4 address is 'a.b.c.d'<br />
Format of IPv6 address is 'a:b:c:d::e:f'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +SNTPERR

##### Description

**SNTP error.**

| AEC                     | Description |
|-------------------------|-------------|
| +SNTPERR:\<ERROR_CODE\> | SNTP error  |

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
<td style="text-align: left;"><p>Integer<br />
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

### Introduction:

#### Reading Socket Data

There are four methods of reading data from a socket, two polled and two asynchronous methods. Polling involves the [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) command and [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT)/[+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AECs. Asynchronous methods involve the [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT)/[+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AECs.

##### Basic SOCKRD/AEC method:

[+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) or [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AECs from the DCE notify the DTE that data is available to be read. The DTE then sends a [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) command with OUTPUT_MODE of 1 or 2 to read a number of bytes from the DCE. After the [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) response further [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) or [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AECs will update the available pending data.

**See example [Basic socket read](#EXAMPLE_SOCKRD_1)**

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,15</strong></td>
<td>Indicates 15 bytes are present</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>=6,1,10</strong></td>
<td>Read 10 bytes in ASCII mode</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>:6,10,"1234567890"</strong></td>
<td>10 bytes returned</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,7</strong></td>
<td>An additional 2 bytes have been received</td>
</tr>
</tbody>
</table>

##### In-band SOCKRD/AEC method:

As with the basic [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) method, [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) or [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) announce the presence of data to be read from a SOCKET. If [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) OUTPUT_MODE 3 is used the resulting [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) response will include the pending data information in the response and no further AECs will be sent until all data has been consumed.

**See example [In-band socket read](#EXAMPLE_SOCKRD_2)**

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,20</strong></td>
<td>Indicates 20 bytes have been received</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>=6,3,10</strong></td>
<td>Read 10 bytes in ASCII mode with extended information</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>:6,10,10,"1234567890"</strong></td>
<td>10 bytes returned, indicates 10 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>=6,3,4</strong></td>
<td>Read 4 bytes in ASCII mode with extended information</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>:6,4,6,"abcd"</strong></td>
<td>4 bytes returned, indicates 6 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

##### Simple Asynchorous method:

By configuring the [+SOCKC](#AN_CMD_AT_SOCKET_SOCKC) [ASYNC_MAX_FRM_SZ](#AN_CMD_SOCKC_STORE_ID_ASYNC_MAX_FRM_SZ) parameter of a socket the DTE can set the maximum frame size of data to be received asynchronously from the DCE.

> [!NOTE]
> For UDP sockets, if the [ASYNC_MAX_FRM_SZ](#AN_CMD_SOCKC_STORE_ID_ASYNC_MAX_FRM_SZ) value is smaller than the size of a datagram, the remaining data from the datagram will be lost.

When the [ASYNC_MAX_FRM_SZ](#AN_CMD_SOCKC_STORE_ID_ASYNC_MAX_FRM_SZ) parameter is set, the DCE will send received socket data to the DTE without polling from [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD), the data is included in an expanded form of [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) or [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AEC.

**See example [Simple asynchronous socket read](#EXAMPLE_SOCKRXT_1)**

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,102,1500</strong></td>
<td>Configure socket ASYNC_MAX_FRM_SZ to be 1500 bytes</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,10,"1234567890"</strong></td>
<td>10 bytes received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,4,"abcd"</strong></td>
<td>4 bytes received</td>
</tr>
</tbody>
</table>

##### Acknowledged Asynchronous method:

Extending the simple asynchronous method, if the [ASYNC_WIN_SZ](#AN_CMD_SOCKC_STORE_ID_ASYNC_WIN_SZ) parameter of a socket is also set the DCE will use a sliding window protocol to send data to the DTE. In addition to the data included in the [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) or [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AEC a sequence number is added, this represents the sequence number of the first byte of the data provided.

The DCE will continue to send data via AEC until [ASYNC_WIN_SZ](#AN_CMD_SOCKC_STORE_ID_ASYNC_WIN_SZ) bytes have been transmitted, after which transmission will cease. To resume transmission the DTE must update the value of [+SOCKC](#AN_CMD_AT_SOCKET_SOCKC) parameter [ASYNC_NEXT_SN](#AN_CMD_SOCKC_STORE_ID_ASYNC_NEXT_SN) to acknowledge reception of data from the DCE, once this value has been updated the DCE will continue to send more data until [ASYNC_NEXT_SN](#AN_CMD_SOCKC_STORE_ID_ASYNC_NEXT_SN) + [ASYNC_WIN_SZ](#AN_CMD_SOCKC_STORE_ID_ASYNC_WIN_SZ) bytes have been received.

The DTE does not need to wait until transmission has ceased before updating [ASYNC_NEXT_SN](#AN_CMD_SOCKC_STORE_ID_ASYNC_NEXT_SN), this can be done at any time and will ensure the transmission window remains open for subsequent [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) or [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AECs.

Using this method the DTE can ensure that buffer space is available for receiving data transmission while still receiving data as it arrives at the DCE.

**See example [Acknowledged asynchronous socket read](#EXAMPLE_SOCKRXT_2)**

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,102,1500</strong></td>
<td>Configure socket ASYNC_MAX_FRM_SZ to be 1500 bytes</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,101,8</strong></td>
<td>Configure socket ASYNC_WIN_SZ to be 8 bytes</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,8,0,"12345678"</strong></td>
<td>8 bytes received, sequence number 0 to 7</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,100,8</strong></td>
<td>Configure ASYNC_NEXT_SN to be 8</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,8,8,"90abcdef"</strong></td>
<td>8 bytes received, sequence number 8 to 15</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,100,12</strong></td>
<td>Configure ASYNC_NEXT_SN to be 12</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,4,16,"ghij"</strong></td>
<td>4 bytes received, sequence number 16 to 19</td>
</tr>
</tbody>
</table>

---
### Command Reference:

<a id="AN_CMD_AT_SOCKET_SOCKO"></a>
#### +SOCKO

##### Description

This command is used to open a new socket.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKO=&lt;PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>Open a socket<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKO=&lt;PROTOCOL&gt;,&lt;PROTOCOL_VERSION&gt;</p></td>
<td style="text-align: left;"><p>Open a socket (specifying IP protocol)<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The protocol to use<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UDP.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>TCP.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROTOCOL_VERSION&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>IP protocol version<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>IPv4.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>IPv6.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response           | Description          |
|--------------------|----------------------|
| +SOCKO:\<SOCK_ID\> | Socket open response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKBL"></a>
#### +SOCKBL

##### Description

This command is used to bind a socket to a local port.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKBL=&lt;SOCK_ID&gt;,&lt;LCL_PORT&gt;</p></td>
<td style="text-align: left;"><p>Bind to a local port<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKBL=&lt;SOCK_ID&gt;,&lt;LCL_PORT&gt;,&lt;PEND_SKTS&gt;</p></td>
<td style="text-align: left;"><p>Bind to a local port with number of connections<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LCL_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The local port number to use<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_SKTS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending sockets connections<br />
<br />
Valid range is 1 to 10<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKBR"></a>
#### +SOCKBR

##### Description

This command is used to bind a socket to a remote address.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKBR=&lt;SOCK_ID&gt;,&lt;RMT_ADDR&gt;,&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Bind to a remote port<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>The address of the remote device<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The port number on the remote device<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SOCKBM

##### Description

This command is used to bind a socket to a multicast group.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKBM=&lt;SOCK_ID&gt;,&lt;MCAST_ADDR&gt;,&lt;MCAST_PORT&gt;</p></td>
<td style="text-align: left;"><p>Bind to a multicast port<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MCAST_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>The address of the multicast group<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MCAST_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The port number of the multicast group<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKTLS"></a>
#### +SOCKTLS

##### Description

This command is used to enable TLS on a socket.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKTLS=&lt;SOCK_ID&gt;,&lt;TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Apply TLS configuration<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>TLS certificate configuration<br />
<br />
Valid range is 0 to 4<br />
</p></td>
</tr>
</tbody>
</table>

| Response             | Description |
|----------------------|-------------|
| +SOCKTLS:\<SOCK_ID\> | TLS succeed |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKWR"></a>
#### +SOCKWR

##### Description

This command is used to send data over a socket that is bound to a remote address and port number.

If no [DATA](#AN_CMD_AT_SOCKET_SOCKWR_DATA) parameter is supplied to the [+SOCKWR](#AN_CMD_AT_SOCKET_SOCKWR) command the DCE will enter raw binary mode and will remain in that mode until the specified length of binary data has been received from the DTE.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKWR=&lt;SOCK_ID&gt;,&lt;LENGTH&gt;,&lt;SEQ_NUM&gt;,&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Socket write with data and sequence number<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKWR=&lt;SOCK_ID&gt;,&lt;LENGTH&gt;,&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Socket write with data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKWR=&lt;SOCK_ID&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Socket write, data to follow<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The length of the data to send<br />
<br />
Valid range is 0 to 1460<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEQ_NUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Sequence number of first byte<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_SOCKET_SOCKWR_DATA"></span>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>The data to send<br />
Maximum length of string is 1460<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKWRTO"></a>
#### +SOCKWRTO

##### Description

This command is used to send data to an arbitrary destination using the connectionless UDP protocol.

If no [DATA](#AN_CMD_AT_SOCKET_SOCKWRTO_DATA) parameter is supplied to the [+SOCKWRTO](#AN_CMD_AT_SOCKET_SOCKWRTO) command the DCE will enter raw binary mode and will remain in that mode until the specified length of binary data has been received from the DTE.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKWRTO=&lt;SOCK_ID&gt;,&lt;RMT_ADDR&gt;,&lt;RMT_PORT&gt;,&lt;LENGTH&gt;,&lt;SEQ_NUM&gt;,&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Socket write to socket with data and sequence number<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKWRTO=&lt;SOCK_ID&gt;,&lt;RMT_ADDR&gt;,&lt;RMT_PORT&gt;,&lt;LENGTH&gt;,&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Socket write to socket with data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKWRTO=&lt;SOCK_ID&gt;,&lt;RMT_ADDR&gt;,&lt;RMT_PORT&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Socket write to socket, data to follow<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>The address of the remote device<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The port number on the remote device<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The length of the data to send<br />
<br />
Valid range is 0 to 1472<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEQ_NUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Sequence number of first byte<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_SOCKET_SOCKWRTO_DATA"></span>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>The data to send<br />
Maximum length of string is 1472<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKRD"></a>
#### +SOCKRD

##### Description

This command is used to read data from a socket.

Two AECs present notification of data received by the DCE:

- [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) indicates UDP data has been received.

- [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) indicates TCP data has been received.

The DTE is responsible for retrieving the datagram/stream data via the [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) command.

For TCP sockets the DCE will indicate, via [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT), the number of bytes of data which are currently available for reading via the [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) command. The DCE may issue multiple [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) AECs as data is received. When requesting data via the [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) command the DTE may receive less data than request, the number of bytes provided by the DCE will be declared in the [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) response before the data is presented. The DTE may request less data than that declared by the [+SOCKRXT](#AN_AEC_AT_SOCKET_SOCKRXT) AEC as being available, the remaining data will be available for subsequent reading.

For UDP sockets the DCE will indicate, via [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU), the number of bytes of data which were received in the oldest datagram received by the DCE. Only a single [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) will be issued by the DCE even if subsequent UDP datagrams are received. Reading data from the UDP socket via the [+SOCKRD](#AN_CMD_AT_SOCKET_SOCKRD) command will read and discard the current datagram, if less data is requested than was indicated by the [+SOCKRXU](#AN_AEC_AT_SOCKET_SOCKRXU) AEC the remaining unread data in the datagram will be discarded.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKRD=&lt;SOCK_ID&gt;,&lt;OUTPUT_MODE&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Socket read<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OUTPUT_MODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The format the DTE wishes to receive the data<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ASCII or hex string.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Binary.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>ASCII or hex string with extended information.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes the DTE wishes to read<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +SOCKRD:\<SOCK_ID\>,\<LENGTH\>,\<DATA\> | Socket read response |
| +SOCKRD:\<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<DATA\> | Socket read response (TCP extended) |
| +SOCKRD:\<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<PEND_DATAGRAM\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<DATA\> | Socket read response (UDP extended) |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATAGRAM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending datagrams<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKRDBUF"></a>
#### +SOCKRDBUF

##### Description

This command is used to read data from a socket buffer (UDP only).

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKRDBUF=&lt;SOCK_ID&gt;,&lt;OUTPUT_MODE&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Socket read<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OUTPUT_MODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The format the DTE wishes to receive the data<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ASCII or hex string.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Binary.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>ASCII or hex string with extended information.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes the DTE wishes to read<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +SOCKRDBUF:\<SOCK_ID\>,\<LENGTH\>,\<DATA\> | Socket read response |
| +SOCKRDBUF:\<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<DATA\> | Socket read response (TCP extended) |
| +SOCKRDBUF:\<SOCK_ID\>,\<LENGTH\>,\<PEND_DATA\>,\<PEND_DATAGRAM\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<DATA\> | Socket read response (UDP extended) |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATAGRAM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending datagrams<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SOCKCL

##### Description

This command is used to close a socket.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKCL=&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Close socket<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

| Response            | Description           |
|---------------------|-----------------------|
| +SOCKCL:\<SOCK_ID\> | Socket close response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SOCKLST

##### Description

This command is used to present a list of the DCE’s open sockets/connections.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKLST</p></td>
<td style="text-align: left;"><p>List all sockets<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKLST=&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>List socket<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +SOCKLST:\<SOCK_ID\>,\<PROTOCOL\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<LCL_PORT\> | Socket list response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The protocol in use<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UDP.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>TCP.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LCL_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Local port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_SOCKET_SOCKC"></a>
#### +SOCKC

##### Description

This command is used to read or set the socket configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SOCKC</p></td>
<td style="text-align: left;"><p>Query range of SOCK_ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKC=&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKC=&lt;SOCK_ID&gt;,&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SOCKC=&lt;SOCK_ID&gt;,&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SOCK_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response              | Description   |
|-----------------------|---------------|
| +SOCKC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;SO_LINGER&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Socket linger enable/disable (TCP)<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enable.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;SO_NODELAY&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Socket no delay (TCP)<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enable.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;SO_KEEPALIVE&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Socket keep alive timeout (TCP)<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;SO_RCVBUF&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Socket receive buffer size (TCP)<br />
<br />
Valid range is 1460 to 32768<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>&lt;SO_SNDBUF&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Socket transmit buffer size (TCP)<br />
<br />
Valid range is 1460 to 32768<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>32</p></td>
<td style="text-align: left;"><p>&lt;IP_TOS&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Socket Type of Service (TCP/UDP)<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0x00</p></td>
<td style="text-align: left;"><p>Normal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x04</p></td>
<td style="text-align: left;"><p>Reliability.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x08</p></td>
<td style="text-align: left;"><p>Throughput.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x10</p></td>
<td style="text-align: left;"><p>Low delay.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_SOCKC_STORE_ID_ASYNC_NEXT_SN"></span> 100</p></td>
<td style="text-align: left;"><p>&lt;ASYNC_NEXT_SN&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Async next sequence number<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_SOCKC_STORE_ID_ASYNC_WIN_SZ"></span> 101</p></td>
<td style="text-align: left;"><p>&lt;ASYNC_WIN_SZ&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Async window size<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_SOCKC_STORE_ID_ASYNC_MAX_FRM_SZ"></span> 102</p></td>
<td style="text-align: left;"><p>&lt;ASYNC_MAX_FRM_SZ&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Async maximum frame size<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_SOCKET_SOCKIND"></a>
#### +SOCKIND

##### Description

**Socket established.**

| AEC | Description |
|----|----|
| +SOCKIND:\<SOCK_ID\>,\<LCL_ADDR\>,\<LCL_PORT\>,\<RMT_ADDR\>,\<RMT_PORT\> | TCP connection established |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LCL_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Local address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LCL_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Local port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
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
#### +SOCKRXT

##### Description

**TCP receive.**

| AEC | Description |
|----|----|
| +SOCKRXT:\<SOCK_ID\>,\<PEND_DATA\> | TCP receive (polled) |
| +SOCKRXT:\<SOCK_ID\>,\<LENGTH\>,\<DATA\> | TCP receive (async) |
| +SOCKRXT:\<SOCK_ID\>,\<LENGTH\>,\<SEQ_NUM\>,\<DATA\> | TCP receive (async reliable) |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEQ_NUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
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
#### +SOCKRXU

##### Description

**UDP receive.**

| AEC | Description |
|----|----|
| +SOCKRXU:\<SOCK_ID\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<PEND_DATA\>,\<PEND_DATAGRAM\> | UDP receive (polled) |
| +SOCKRXU:\<SOCK_ID\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<LENGTH\>,\<DATA\> | UDP receive (async) |
| +SOCKRXU:\<SOCK_ID\>,\<RMT_ADDR\>,\<RMT_PORT\>,\<LENGTH\>,\<SEQ_NUM\>,\<DATA\> | UDP receive (async reliable) |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_ADDR&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
IPv4 or IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Remote address<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RMT_PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Remote port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATAGRAM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending datagrams<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Socket data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SEQ_NUM&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Sequence number of first byte<br />
<br />
Unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SOCKCL

##### Description

**Socket close.**

| AEC                 | Description           |
|---------------------|-----------------------|
| +SOCKCL:\<SOCK_ID\> | Socket close response |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_SOCKET_SOCKTLS"></a>
#### +SOCKTLS

##### Description

**TLS success.**

| AEC                  | Description |
|----------------------|-------------|
| +SOCKTLS:\<SOCK_ID\> | TLS succeed |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SOCKERR

##### Description

**Socket error.**

| AEC                                 | Description     |
|-------------------------------------|-----------------|
| +SOCKERR:\<SOCK_ID\>,\<ERROR_CODE\> | TCP bind failed |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The socket ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

Opening a TCP server socket
<a id="EXAMPLE_SOCKO_1"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>=2</strong></td>
<td>Open a TCP socket</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>:5</strong></td>
<td>Socket ID 5 created</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKBL">+SOCKBL</a>=5,5678</strong></td>
<td>Bind socket to local port 5678</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKIND">+SOCKIND</a>:6,"1.2.3.4",5678,"11.22.33.44",12345</strong></td>
<td>New socket connection on port 5678</td>
</tr>
</tbody>
</table>

Basic socket read
<a id="EXAMPLE_SOCKRD_1"></a>

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,15</strong></td>
<td>Indicates 15 bytes are present</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>=6,1,10</strong></td>
<td>Read 10 bytes in ASCII mode</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>:6,10,"1234567890"</strong></td>
<td>10 bytes returned</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,7</strong></td>
<td>An additional 2 bytes have been received</td>
</tr>
</tbody>
</table>

In-band socket read
<a id="EXAMPLE_SOCKRD_2"></a>

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,20</strong></td>
<td>Indicates 20 bytes have been received</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>=6,3,10</strong></td>
<td>Read 10 bytes in ASCII mode with extended information</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>:6,10,10,"1234567890"</strong></td>
<td>10 bytes returned, indicates 10 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>=6,3,4</strong></td>
<td>Read 4 bytes in ASCII mode with extended information</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>:6,4,6,"abcd"</strong></td>
<td>4 bytes returned, indicates 6 bytes remain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Simple asynchronous socket read
<a id="EXAMPLE_SOCKRXT_1"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,102,1500</strong></td>
<td>Configure socket ASYNC_MAX_FRM_SZ to be 1500 bytes</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,10,"1234567890"</strong></td>
<td>10 bytes received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,4,"abcd"</strong></td>
<td>4 bytes received</td>
</tr>
</tbody>
</table>

Reliable asynchronous socket read
<a id="EXAMPLE_SOCKRXT_2"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,102,1500</strong></td>
<td>Configure socket ASYNC_MAX_FRM_SZ to be 1500 bytes</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,101,8</strong></td>
<td>Configure socket ASYNC_WIN_SZ to be 8 bytes</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,8,0,"12345678"</strong></td>
<td>8 bytes received, sequence number 0 to 7</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,100,8</strong></td>
<td>Configure ASYNC_NEXT_SN to be 8</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,8,8,"90abcdef"</strong></td>
<td>8 bytes received, sequence number 8 to 15</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKC">+SOCKC</a>=6,100,12</strong></td>
<td>Configure ASYNC_NEXT_SN to be 12</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXT">+SOCKRXT</a>:6,4,16,"ghij"</strong></td>
<td>4 bytes received, sequence number 16 to 19</td>
</tr>
</tbody>
</table>

Set TLS configuration 1 for TLS client
<a id="EXAMPLE_SOCKTLSCLI"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,41,1</strong></td>
<td>Enable server domain verification</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,6,"ServerDomain"</strong></td>
<td>Specify server domain name</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,40,1</strong></td>
<td>Enable server authentication</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,1,"ServerRootCACert"</strong></td>
<td>Specify file name of CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,2,"MyClientCert"</strong></td>
<td>Specify file name of client certificate (required if server authenticates the client)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,3,"MyClientPrivateKey"</strong></td>
<td>Specify file name of client private key (required if server authenticates the client)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Open a TLS client socket with AT+SOCK
<a id="EXAMPLE_12de0326b22680d3b9cc3d612dba34e5f4d023fe"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>=2</strong></td>
<td>Open a TCP socket</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>:17603</strong></td>
<td>Socket created</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKTLS">+SOCKTLS</a>=17603,1</strong></td>
<td>Upgrade socket to TLS, using configuration 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKBR">+SOCKBR</a>=17603,"example.com",443</strong></td>
<td>Bind socket to server</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKIND">+SOCKIND</a>:17603,"1.2.3.4",65333,"5.6.7.8",443</strong></td>
<td>Socket connected</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKTLS">+SOCKTLS</a>:17603</strong></td>
<td>Socket upgraded to TLS</td>
</tr>
</tbody>
</table>

Set TLS configuration 2 for TLS server
<a id="EXAMPLE_SOCKTLSSRV"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,2,"MyServerCertChain"</strong></td>
<td>Specify file name of server certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,3,"MyServerPrivateKey"</strong></td>
<td>Specify file name of server private key</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,8,"MyDhParams"</strong></td>
<td>Specify file name of server DH parameters (DHE cipher suite only)</td>
</tr>
<tr>
<td>←</td>
<td><code>0K</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,40,0</strong></td>
<td>Disable client authentication</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,41,0</strong></td>
<td>Disable client domain name verification</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Open a TLS server socket with AT+SOCK
<a id="EXAMPLE_a70e12e9f2deb08dda4c674bca8584fd9c59e257"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>=2</strong></td>
<td>Open a TCP socket</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>:16037</strong></td>
<td>Socket created</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKTLS">+SOCKTLS</a>=16037,2</strong></td>
<td>Upgrade socket to TLS, using configuration 2</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKBL">+SOCKBL</a>=16037,443</strong></td>
<td>Bind socket to local port 443</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKIND">+SOCKIND</a>:16037,"1.2.3.4",443,"11.22.33.44",12345</strong></td>
<td>New socket connection on port 443</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKTLS">+SOCKTLS</a>:16037</strong></td>
<td>Socket upgraded to TLS</td>
</tr>
</tbody>
</table>

Reading partial datagram
<a id="EXAMPLE_SOCKRDBUF"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>=1</strong></td>
<td>Open a UDP socket</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>:7</strong></td>
<td>Socket ID 7 created</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKBL">+SOCKBL</a>=7,1234</strong></td>
<td>Bind socket to port 1234</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKRXU">+SOCKRXU</a>:7,"1.2.3.4",1234,100,1</strong></td>
<td>100 bytes datagram received</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRDBUF">+SOCKRDBUF</a>=7,1,10</strong></td>
<td>Read first 10 bytes of datagram</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRDBUF">+SOCKRDBUF</a>=7,10,\[11223344556677889900\]</strong></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRDBUF">+SOCKRDBUF</a>=7,1,10</strong></td>
<td>Read second 10 bytes of datagram</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRDBUF">+SOCKRDBUF</a>=7,10,\[AABBCCDDEEFF11223344\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKRD">+SOCKRD</a>=7,1,10</strong></td>
<td>Read first 10 bytes of next datagram and discard remaining (and buffered)</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKRDBUF">+SOCKRDBUF</a>=7,10,\[1234567890ABCDEF0011\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_TIME"></a>
## TIME (Module ID = 16)

### Command Reference:

<a id="AN_CMD_AT_TIME_TIME"></a>
#### +TIME

##### Description

This command is used to set or query the system time.

Three formats of time are supported, two are in UTC seconds and one is a string based on RFC3339 / ISO-8601 format:

1.  UNIX timestamp - UTC seconds since 1st January 1970

2.  NTP time - UTC seconds since 1st January 1900

3.  RFC3339 / ISO-8601 - String representation of date/time

RFC3338 / ISO-8601 format represents the time as:

    YYYY-MM-DDTHH:MM:SS.ssZ

For example:

    2019-02-28T12:34:56.01Z - 28th February 2019, 12:34 PM 56.01 seconds (UTC+0)

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+TIME</p></td>
<td style="text-align: left;"><p>Time query in current format<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TIME=&lt;FORMAT&gt;</p></td>
<td style="text-align: left;"><p>Time query in specified format<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TIME=&lt;FORMAT&gt;,&lt;UTC_SEC&gt;</p></td>
<td style="text-align: left;"><p>Time set in UTC seconds<br />
<br />
<a href="#AN_CMD_AT_TIME_TIME_FORMAT">FORMAT</a> must be 1 or 2</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TIME=&lt;FORMAT&gt;,&lt;DATE_TIME&gt;</p></td>
<td style="text-align: left;"><p>Time set in RFC3339/ISO-8601 format<br />
<br />
<a href="#AN_CMD_AT_TIME_TIME_FORMAT">FORMAT</a> must be 3</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_TIME_TIME_FORMAT"></span>&lt;FORMAT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Format of time<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>UTC seconds (epoch 01/01/1970 - UNIX timestamp).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>UTC seconds (epoch 01/01/1900 - NTP time).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>RFC3339 / ISO-8601 format.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;UTC_SEC&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>UTC seconds<br />
<br />
Unsigned 32-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATE_TIME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Date/time in format YYYY-MM-DDTHH:MM:SS.00Z<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_TIME_TIME"></a>
#### +TIME

##### Description

**Time report.**

| AEC            | Description |
|----------------|-------------|
| +TIME:\<TIME\> | Time report |

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
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
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

The RNWF02 can establish a TLS session in either client mode or server mode. The TLS configuration parameters described in this module are used in conjunction with the [SOCK](#AN_MOD_SOCKET), [MQTT](#AN_MOD_MQTT), and [WSTA](#AN_MOD_WSTA) modules to enable secure connections.

#### TLS configuration

Set TLS parameters using the [+TLSC](#AN_CMD_AT_TLS_TLSC) and [+TLSCSC](#AN_CMD_AT_TLS_TLSCSC) commands.

See examples [Basic TLS client configuration](#EXAMPLE_SOCKTLSCLI) and [Basic TLS server configuration](#EXAMPLE_SOCKTLSSRV).

##### Certificate and Private Key

The X.509 certificate and the corresponding private key are required for the peer to authenticate the DCE.

The certificate file name can be specified via [CERT_NAME](#AN_CMD_TLSC_STORE_ID_CERT_NAME) and must be in PEM or DER format. If the file contains multiple certificates, it must be in PEM format. The private key file name can be specified via [PRI_KEY_NAME](#AN_CMD_TLSC_STORE_ID_PRI_KEY_NAME) and must be in PEM or DER format. If the private key is encrypted, the password must also be provided via [PRI_KEY_PASSWORD](#AN_CMD_TLSC_STORE_ID_PRI_KEY_PASSWORD).

Certificate and private key are always required for TLS server mode. For client mode, they are required if the server authenticates the client.

##### Server Name

The TLS Server Name Indication (SNI) extension allows a client to specify the hostname it is connecting to during the TLS handshake. This enables a server hosting multiple domains on the same IP address to present the correct certificate.

The server name is configured via [SERVER_NAME](#AN_CMD_TLSC_STORE_ID_SERVER_NAME). This parameter only applies to client mode.

##### Peer authentication

Peer authentication validates the peer’s certificate chain against trusted CA certificates provided in the CA certificate file.

When peer authentication is enabled via [PEER_AUTH](#AN_CMD_TLSC_STORE_ID_PEER_AUTH), a valid CA certificate file name must be provided via [CA_CERT_NAME](#AN_CMD_TLSC_STORE_ID_CA_CERT_NAME). If the file contains multiple certificates, it must be in PEM format.

Peer authentication is recommended in client mode.

##### Domain Name Verification

Domain name verification confirms the peer’s certificate was issued for the expected server by matching the configured domain name against the certificate’s Subject Alternative Name (SAN), or Common Name (CN) if no SAN is present.

When domain name verification is enabled via [PEER_DOMAIN_VERIFY](#AN_CMD_TLSC_STORE_ID_PEER_DOMAIN_VERIFY), the expected domain name must be provided via [DOMAIN_NAME](#AN_CMD_TLSC_STORE_ID_DOMAIN_NAME).

Peer domain verification is recommented in client mode.

##### Cipher Suites

A cipher suite defines the algorithms used for key exchange, data encryption, and message authentication during a TLS session. The cipher suites index ([CIPHER_SUITES_IDX](#AN_CMD_TLSC_STORE_ID_CIPHER_SUITES_IDX)) references a cipher suite list configured using the [+TLSCSC](#AN_CMD_AT_TLS_TLSCSC) command.

##### Diffie-Hellman Parameters

Diffie-Hellman (DH) parameters define the prime number and generator used to establish a shared secret between client and server without transmitting the secret itself. The file containing the Diffie-Hellman parameters must be specified via [DH_PARAM_NAME](#AN_CMD_TLSC_STORE_ID_DH_PARAM_NAME) if DHE key exchange cipher suites are enabled. Diffie-Hellman parameters are only required for server mode.

##### Certificate Pinning

Certificate pinning allows specifying a list of expected hash digest/hash algorithm pairs. During the TLS handshake, the peer’s leaf certificate is hashed and compared against the configured digests. If none match, the connection is rejected.

Certificate pinning provides additional security beyond CA-based authentication by ensuring connections are only made to servers with specific known certificates, protecting against compromised CAs or misissued certificates.

See example [configuring certificate digests](#EXAMPLE_TLS_DIGEST)

##### External crypto operations

TLS client authentication allows a server to verify the client’s identity by requesting the client to sign a message with its private key, which is verified against the public key in the X.509 certificate. Signing operations can be delegated to an external crypto device via the [EXTCRYPTO](#AN_MOD_EXTCRYPTO) module.

When signing is enabled via [EXTCRYPTO_OPS](#AN_CMD_TLSC_STORE_ID_EXTCRYPTO_OPS), only the certificate file must be provided via [CERT_NAME](#AN_CMD_TLSC_STORE_ID_CERT_NAME). The private key is not required as it resides in the external crypto device.

See example [TLS client configuration with external crypto device](#EXAMPLE_EXTCRYPTO_TLS)

##### Server Renegotiation Extension

The TLS renegotiation info extension was introduced to address the TLS renegotiation vulnerability (CVE-2009-3555). Servers that are patched against this vulnerability include the renegotiation info extension during the TLS handshake.

When the server renegotiation info ([SERVER_RENEG_INFO](#AN_CMD_TLSC_STORE_ID_SERVER_RENEG_INFO)) is configured as "required", the client rejects connections to servers that do not provide it. Othwerise, the client will connect even if the server does not send the extension. "required" is the recommented setting unless connecting to legacy servers that do not support the security patch. This option is only applicable to client mode.

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

To assist with debugging TLS issues, error codes from wolfSSL can be obtained by enabling logging via [+SYSLOGC](#AN_CMD_AT_SYSLOG_SYSLOGC).

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

### Command Reference:

<a id="AN_CMD_AT_TLS_TLSC"></a>
#### +TLSC

##### Description

This command is used to read or set the TLS configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+TLSC</p></td>
<td style="text-align: left;"><p>Query configuration list<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSC=&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSC=&lt;CONF&gt;,&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSC=&lt;CONF&gt;,&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
<br />
<a href="#AN_CMD_AT_TLS_TLSC_ID">ID</a> must not be 9</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSC=&lt;CONF&gt;,&lt;ID&gt;,&lt;DIGEST&gt;,&lt;ALGO&gt;</p></td>
<td style="text-align: left;"><p>Set a hash digest/algorithm pair<br />
<br />
<a href="#AN_CMD_AT_TLS_TLSC_ID">ID</a> must be 9</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSC=&lt;CONF&gt;,&lt;ID&gt;,&lt;DIGEST&gt;</p></td>
<td style="text-align: left;"><p>Clear a hash digest/algorithm pair<br />
<br />
<a href="#AN_CMD_AT_TLS_TLSC_ID">ID</a> must be 9</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Valid range is 1 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_TLS_TLSC_ID"></span>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
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
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>SHA1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>SHA2-256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>SHA2-224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>SHA2-512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>SHA2-384.</p></td>
</tr>
</tbody>
</table>
<p><br />
Valid range is 1 to 5<br />
</p></td>
</tr>
</tbody>
</table>

| Response                | Description   |
|-------------------------|---------------|
| +TLSC:\<CONF\>,\<CONF\> | List response |
| +TLSC:\<ID\>,\<VAL\>    | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Valid range is 1 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_CA_CERT_NAME"></span> 1</p></td>
<td style="text-align: left;"><p>&lt;CA_CERT_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>CA certificate name<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_CERT_NAME"></span> 2</p></td>
<td style="text-align: left;"><p>&lt;CERT_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Certificate name<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_PRI_KEY_NAME"></span> 3</p></td>
<td style="text-align: left;"><p>&lt;PRI_KEY_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Private key name<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_PRI_KEY_PASSWORD"></span> 4</p></td>
<td style="text-align: left;"><p>&lt;PRI_KEY_PASSWORD&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Private key password<br />
Maximum length of string is 64<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_SERVER_NAME"></span> 5</p></td>
<td style="text-align: left;"><p>&lt;SERVER_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Server name<br />
Maximum length of string is 256<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_DOMAIN_NAME"></span> 6</p></td>
<td style="text-align: left;"><p>&lt;DOMAIN_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Domain name<br />
Maximum length of string is 256<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_CIPHER_SUITES_IDX"></span> 7</p></td>
<td style="text-align: left;"><p>&lt;CIPHER_SUITES_IDX&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Cipher suite index<br />
<br />
Valid range is 1 to 2<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_DH_PARAM_NAME"></span> 8</p></td>
<td style="text-align: left;"><p>&lt;DH_PARAM_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Server Diffie-Hellman parameters identifier<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>&lt;PEER_CERT_DIGESTS&gt;</p></td>
<td style="text-align: left;"><p>Complex Value<sup>1</sup><br />
</p></td>
<td style="text-align: left;"><p>List of hash digest/algorithm pairs<br />
This is a multiple value parameter<br />
with an ID range 9.0 to 9.3<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_EXTCRYPTO_OPS"></span> 20</p></td>
<td style="text-align: left;"><p>&lt;EXTCRYPTO_OPS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Crypto operations to be done externally<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>None.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Signing.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>&lt;SIGN_TYPES&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Types of signing to be done externally<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ECDSA.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_PEER_AUTH"></span> 40</p></td>
<td style="text-align: left;"><p>&lt;PEER_AUTH&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Peer authentication<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Peer authentication is disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Peer authentication is enabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_PEER_DOMAIN_VERIFY"></span> 41</p></td>
<td style="text-align: left;"><p>&lt;PEER_DOMAIN_VERIFY&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Peer domain verification<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Peer domain name verification is disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Peer domain name verification is enabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_SERVER_RENEG_INFO"></span> 42</p></td>
<td style="text-align: left;"><p>&lt;SERVER_RENEG_INFO&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Client mode: require renegotiation info from server<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Do not require renegotiation info from server.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Require renegotiation info from server.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_TLSC_STORE_ID_SESSION_CACHING"></span> 43</p></td>
<td style="text-align: left;"><p>&lt;SESSION_CACHING&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Client mode: cache and reuse session IDs<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Do not reuse session IDs.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Attempt to reuse session IDs.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
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
<a id="AN_CMD_AT_TLS_TLSCSC"></a>
#### +TLSCSC

##### Description

This command is used to read or set the TLS cipher suite configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+TLSCSC</p></td>
<td style="text-align: left;"><p>Query configuration list<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSCSC=&lt;CSL_IDX&gt;</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSCSC=&lt;CSL_IDX&gt;,&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+TLSCSC=&lt;CSL_IDX&gt;,&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CSL_IDX&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Cipher suite list index<br />
<br />
Valid range is 1 to 2<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response               | Description   |
|------------------------|---------------|
| +TLSCSC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;CIPHER_SUITES&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Cipher suites<br />
<br />
Positive unsigned 16-bit value<br />
This is a multiple value parameter<br />
with an ID range 1.0 to 1.31<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;CIPHER_SUITES_AVAIL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Cipher suites available<br />
<br />
Positive unsigned 16-bit value<br />
This is a multiple value parameter<br />
with an ID range 2.0 to 2.31<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +TLSERR

##### Description

**TLS error.**

| AEC                             | Description |
|---------------------------------|-------------|
| +TLSERR:\<CONF\>,\<ERROR_CODE\> | TLS error   |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Valid range is 1 to 4<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

Peer certificate digest pinning with [+TLSC](#AN_CMD_AT_TLS_TLSC)
<a id="EXAMPLE_TLS_DIGEST"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,9,\[000102030405060708090A0B0C0D0E0F00010203\],1</strong></td>
<td>Add SHA1 000102…​ certificate digest</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,9,\[101112131415161718191A1B1C1D1E1F10111213\],1</strong></td>
<td>Add SHA1 101112…​ certificate digest</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,9</strong></td>
<td>List certificate digests</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>:9.0,\[000102030405060708090A0B0C0D0E0F00010203\],1</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>:9.1,\[101112131415161718191A1B1C1D1E1F10111213\],1</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,9,\[\]</strong></td>
<td>Clear certificate digest list</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,9</strong></td>
<td>List certificate digests</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_WAP"></a>
## WAP (Module ID = 18)

### Command Reference:

#### +WAPC

##### Description

This command is used to read or set the DCE’s hotspot access point configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WAPC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WAPC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WAPC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response             | Description   |
|----------------------|---------------|
| +WAPC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;SSID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Network Name<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;SEC_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Security Type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2 Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2 Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3 Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3 Personal.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;CREDENTIALS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Credentials required for connecting to the network of the security type specified<br />
Maximum length of string is 128<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;CHANNEL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The channel on which to set up the network<br />
<br />
Valid range is 1 to 13<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>&lt;HIDDEN&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Visibility of the network<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Not hidden, SSID is broadcast in beacons.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Hidden, SSID is not broadcast.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>&lt;NETIF_IDX&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Network interface index<br />
<br />
Valid range is 0 to 1<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>&lt;REKEY_INTERVAL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Specify the time in seconds that must pass before each re-key attempt<br />
<br />
Valid range is 60 to 86400<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>50</p></td>
<td style="text-align: left;"><p>&lt;MFP_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Management Frame Protection configuration<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>MFP Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>MFP Enabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>MFP Required.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
#### +WAP

##### Description

This command is used to enable the DCE’s hotspot access point functionality.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WAP</p></td>
<td style="text-align: left;"><p>Read status of AP function<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WAP=&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Set state of AP function<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>State of the hotspot feature<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enable.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response       | Description                |
|----------------|----------------------------|
| +WAP:\<STATE\> | Query state (disconnected) |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Connected state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +WAPAIP

##### Description

**STA IP address assignment.**

| AEC                                 | Description                  |
|-------------------------------------|------------------------------|
| +WAPAIP:\<ASSOC_ID\>,\<IP_ADDRESS\> | Assignment of STA IP address |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;IP_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>IP address assigned<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +WAPSC

##### Description

**STA connected.**

| AEC                                 | Description     |
|-------------------------------------|-----------------|
| +WAPSC:\<ASSOC_ID\>,\<MAC_ADDRESS\> | Station connect |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MAC_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>MAC address of the STA<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +WAPSD

##### Description

**STA disconnected.**

| AEC                                 | Description        |
|-------------------------------------|--------------------|
| +WAPSD:\<ASSOC_ID\>,\<MAC_ADDRESS\> | Station disconnect |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MAC_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>MAC address of the STA<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +WAPERR

##### Description

**AP error.**

| AEC                    | Description |
|------------------------|-------------|
| +WAPERR:\<ERROR_CODE\> | AP error    |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
## WSCN (Module ID = 19)

### Command Reference:

<a id="AN_CMD_AT_WSCN_WSCNC"></a>
#### +WSCNC

##### Description

This command is used to modify or query the behavior of the active scanning function.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WSCNC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WSCNC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WSCNC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response              | Description   |
|-----------------------|---------------|
| +WSCNC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;CHANNEL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Channel to scan (or 0 for all channels)<br />
<br />
Valid range is 1 to 13<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;ACT_SLOT_TIME&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>The time in milliseconds to wait for probe responses<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;PASV_SLOT_TIME&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>The time in milliseconds to wait for beacons<br />
<br />
Unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;NUM_SLOTS&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of scan slots<br />
<br />
Unsigned 8-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>&lt;PROBES_PER_SLOT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of probes sent per active slot<br />
<br />
Unsigned 8-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>&lt;RSSI_THRESH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>RSSI threshold (or 0 for none)<br />
<br />
Signed 8-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>&lt;SEC_FILTER&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Security filter, bitmask of:<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0x01</p></td>
<td style="text-align: left;"><p>Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x02</p></td>
<td style="text-align: left;"><p>Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x04</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x08</p></td>
<td style="text-align: left;"><p>Unknown or unsupported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x10</p></td>
<td style="text-align: left;"><p>WPA or WPA2 Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x20</p></td>
<td style="text-align: left;"><p>WPA2.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x40</p></td>
<td style="text-align: left;"><p>WPA3 or WPA3 Transition Mode.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>&lt;ASYNC_NOTIFY&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Asynchronous notification<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>No scan indication AECs are generated.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Indication AECs are generated.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;FILT_LIST&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>SSID filter list<br />
This is a multiple value parameter<br />
with an ID range 10.0 to 10.3<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>&lt;CHANMASK24&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
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
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>&lt;SCAN_RESULTS&gt;</p></td>
<td style="text-align: left;"><p>Complex Value<sup>1</sup><br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Top scan results from previous scan, ordered by RSSI<br />
This is a multiple value parameter<br />
with an ID range 20.0 to 20.7<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
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
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>-1</p></td>
<td style="text-align: left;"><p>Unknown or unsupported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2-Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3-Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
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
<a id="AN_CMD_AT_WSCN_WSCN"></a>
#### +WSCN

##### Description

This command is used to scan for infrastructure networks in range of the DCE.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WSCN=&lt;ACT_PASV&gt;</p></td>
<td style="text-align: left;"><p>Scan<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ACT_PASV&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Flag indicating active or passive scanning<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Passive scanning.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Active scanning.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_WSCN_WSCNIND"></a>
#### +WSCNIND

##### Description

**Scan results.**

| AEC | Description |
|----|----|
| +WSCNIND:\<RSSI\>,\<SEC_TYPE\>,\<CHANNEL\>,\<BSSID\>,\<SSID\> | Scan indicator |

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
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>-1</p></td>
<td style="text-align: left;"><p>Unknown or unsupported.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2-Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3-Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
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
<a id="AN_AEC_AT_WSCN_WSCNDONE"></a>
#### +WSCNDONE

##### Description

**Scan completed.**

| AEC                       | Description   |
|---------------------------|---------------|
| +WSCNDONE:\<NUM_RESULTS\> | Scan complete |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of results returned in this scan operation<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

Scan for Access Points and filter by security type
<a id="EXAMPLE_WSCN_SECURITY"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=7</strong></td>
<td>Query security filter</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=7,0x77</strong></td>
<td>Security filter 0x77 (all supported security types)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCN">+WSCN</a>=1</strong></td>
<td>Scan for Access Points</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNIND">+WSCNIND</a>:-38,6,11,"00:01:02:03:04:05","SSID1"</strong></td>
<td>AP on network "SSID1" found on channel 11. For connecting, the recommended security type is WPA2-Enterprise Mixed Mode</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNIND">+WSCNIND</a>:-38,6,6,"00:02:04:06:08:0A","SSID1"</strong></td>
<td>AP on network "SSID1" found on channel 6. For connecting, the recommended security type is WPA2-Enterprise Mixed Mode</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNIND">+WSCNIND</a>:-40,4,1,"00:03:06:09:0C:0F","SSID2"</strong></td>
<td>AP on network "SSID2" found on channel 1. For connecting, the recommended security type is WPA3-Personal Transition Mode</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNIND">+WSCNIND</a>:-35,5,6,"00:04:08:0C:10:14","SSID3"</strong></td>
<td>AP on network "SSID3" found on channel 6. For connecting, the recommended security type is WPA3-Personal</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNDONE">+WSCNDONE</a>:4</strong></td>
<td>Scan completed, 4 results found</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=7,0x21</strong></td>
<td>Set security filter to WPA2-Personal</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCN">+WSCN</a>=1</strong></td>
<td>Scan for Access Points</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNIND">+WSCNIND</a>:-41,4,1,"00:03:06:09:0C:0F","SSID2"</strong></td>
<td>AP on network "SSID2" found on channel 1. For connecting, the recommended security type is WPA3-Personal Transition Mode</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNIND">+WSCNIND</a>:-36,5,6,"00:04:08:0C:10:14","SSID3"</strong></td>
<td>AP on network "SSID3" found on channel 6. For connecting, the recommended security type is WPA3-Personal</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNDONE">+WSCNDONE</a>:2</strong></td>
<td>Scan completed, 2 results found</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=7,0x41</strong></td>
<td>Set security filter to WPA3-Personal or WPA3-Personal Transition Mode</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCN">+WSCN</a>=1</strong></td>
<td>Scan for Access Points</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNIND">+WSCNIND</a>:-35,5,6,"00:04:08:0C:10:14","SSID3"</strong></td>
<td>AP on network "SSID3" found on channel 6. For connecting, the recommended security type is WPA3-Personal</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNDONE">+WSCNDONE</a>:1</strong></td>
<td>Scan completed, 1 result found</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=7,0x22</strong></td>
<td>Set security filter to WPA2-Enterprise</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCN">+WSCN</a>=1</strong></td>
<td>Scan for Access Points</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSCN_WSCNDONE">+WSCNDONE</a>:0</strong></td>
<td>Scan completed, 0 results found</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=7</strong></td>
<td>Query security filter</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=7,0x22</strong></td>
<td>Security filter 0x22 (WPA2-Enterprise)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Setting SSID filter with [+WSCNC](#AN_CMD_AT_WSCN_WSCNC)
<a id="EXAMPLE_286d6c7f74c01a7bacc3d6fcaa240ad067b1f736"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=10,"SSID1"</strong></td>
<td>Add SSID1 to filter list</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=10,"SSID2"</strong></td>
<td>Add SSID2 to filter list</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=10,"SSID3"</strong></td>
<td>Add SSID3 to filter list</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=10</strong></td>
<td>List all filters</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>:10.0,"SSID1"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>:10.1,"SSID2"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>:10.2,"SSID3"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=10.1,""</strong></td>
<td>Remove second filter entry (SSID2)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=10</strong></td>
<td>List all filters</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>:10.0,"SSID1"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>:10.1,"SSID3"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSCN_WSCNC">+WSCNC</a>=10,""</strong></td>
<td>Remove all filters</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_WSTA"></a>
## WSTA (Module ID = 20)

### Introduction

The RNWF02 supports a wide range of features when operating as a Wi-Fi station (STA). It is designed for robust connectivity, security, and seamless network integration in a variety of applications.

The [WSTA](#AN_MOD_WSTA) module is used to configure the STA, control STA connection and get information about the STA.

#### Configuring the STA

Set STA parameters using the [+WSTAC](#AN_CMD_AT_WSTA_WSTAC) command.

In order to connect the STA to an Access Point (AP), the following parameters must be set:

- The AP’s network name (SSID): [SSID](#AN_CMD_WSTAC_STORE_ID_SSID)

- The security type (Open, WPA Personal or WPA Enterprise): [SEC_TYPE](#AN_CMD_WSTAC_STORE_ID_SEC_TYPE)

- The security credentials (depending on security type)

Other parameters are optional, with default behaviour if they are not set:

- The AP’s Wi-Fi channel (1-13 or "any"; defaults to "any"): [CHANNEL](#AN_CMD_WSTAC_STORE_ID_CHANNEL)

- The AP’s BSSID: [BSSID](#AN_CMD_WSTAC_STORE_ID_BSSID)

- Management Frame Protection configuration (disabled, enabled or required; defaults to enabled): [MFP_TYPE](#AN_CMD_WSTAC_STORE_ID_MFP_TYPE)

- Disabling of WPA3 Transition modes (defaults to "not modified"): [WPA3_TD](#AN_CMD_WSTAC_STORE_ID_WPA3_TD)

- Connection attempt timeout (defaults to 100ms): [CONN_TIMEOUT](#AN_CMD_WSTAC_STORE_ID_CONN_TIMEOUT)

- Roaming configuration (off, layer 2, or layer 3; defaults to layer 3): [ROAMING](#AN_CMD_WSTAC_STORE_ID_ROAMING)

##### Security types and credentials

Open security provides no authentication or encryption. There are no security credentials to set.

WPA Personal security provides authentication and encryption via a password. WPA2 and WPA3 are supported, including transition and mixed modes. The credentials parameter must be set to the AP’s WPA Personal password: [CREDENTIALS](#AN_CMD_WSTAC_STORE_ID_CREDENTIALS)

WPA Enterprise security provides encryption and various methods for authentication. WPA2 and WPA3 are supported, including transition and mixed modes. See the WPA Enterprise section below for further information about how to set authentication methods and security credentials.

---
##### Roaming

The RNWF02 STA supports Simple Roaming, which enables faster handover between Access Points within an ESSID for maintained connectivity.

Roaming can be configured at two different layers:

- Layer 2 roaming - moving to another SSID, leaving layers 3 (IP) and above unchanged

- Layer 3 roaming - as above but also reconfiguring layer 3 via DHCP

#### Controlling STA connection

Once the STA has been configured appropriately, start and stop the STA connection using the [+WSTA](#AN_CMD_AT_WSTA_WSTA) command.

#### STA information

Query the STA parameters using the [+WSTAC](#AN_CMD_AT_WSTA_WSTAC) command.

Query the STA status using the [+WSTA](#AN_CMD_AT_WSTA_WSTA) command.

During connection:

- The [+WSTALU](#AN_AEC_AT_WSTA_WSTALU) and [+WSTALD](#AN_AEC_AT_WSTA_WSTALD) AECs indicate the Wi-Fi link being established ("up") or lost ("down") respectively. The [+WSTAROAM](#AN_AEC_AT_WSTA_WSTAROAM) AEC indicates a layer 2 roam event (connection lost and regained, possibly to a different AP).

- The [+WSTAAIP](#AN_AEC_AT_WSTA_WSTAAIP) AEC indicates the IP address assigned to the STA. Layer 3 roam events may cause this AEC to be received multiple times, whenever the IP address changes.

---
#### WPA Enterprise

WPA Enterprise significantly enhances Wi-Fi security by using an external authentication server (typically a RADIUS server) to perform user or device authentication dynamically. This process utilises the Extensible Authentication Protocol (EAP), enabling flexible authentication mechanisms beyond entering a simple shared password.

WPA Enterprise typically uses a **two-step process**:

1.  **Establish a secure encrypted tunnel between the Wi-Fi client (STA) and the authentication server.** A TLS (Transport Layer Security) handshake allows the client to authenticate the server. The resulting TLS session provides an encrypted tunnel to protect subsequent communications.

2.  **Authenticate the client securely inside the encrypted tunnel.** After the tunnel is established, a second method (such as MSCHAPv2 or another TLS handshake) allows the server to authenticate the client via the client’s credentials (such as an MSCHAPv2 username and password or a TLS certificate and private key). This client authentication is protected by the encrypted tunnel.

Upon successful authentication, the client and server generate a Pairwise Master Key (PMK). This is used to establish a secure Wi-Fi association between the STA and the Access Point.

##### Supported WPA Enterprise methods

To maximise compatibility with a broad range of Enterprise networks, RNWF02 supports the following tunnel and credential methods:

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

- The AP’s network name (SSID): [SSID](#AN_CMD_WSTAC_STORE_ID_SSID)

- The security type (WPA Enterprise): [SEC_TYPE](#AN_CMD_WSTAC_STORE_ID_SEC_TYPE)

- The unprotected user identity (many servers accept an anonymous identity): [ENT_IDENT_PLAIN](#AN_CMD_WSTAC_STORE_ID_ENT_IDENT_PLAIN)

- The protected user identity: [ENT_IDENT_PROT](#AN_CMD_WSTAC_STORE_ID_ENT_IDENT_PROT)

> [!NOTE]
> The protected user identity parameter may be left unset if the tunnel method parameter is set to "None" or "TTLSv0".

- The client credential type (TLS or MSCHAPv2): [ENT_CRED_TYPE](#AN_CMD_WSTAC_STORE_ID_ENT_CRED_TYPE)

- The TLS configuration index for the tunnel method: [ENT_TUNN_TLS_CONF](#AN_CMD_WSTAC_STORE_ID_ENT_TUNN_TLS_CONF)

> [!NOTE]
> The TLS configuration index for the tunnel method may be left unset if the tunnel method parameter is set to "None".

In addition:

- If the client credential type is TLS, the TLS configuration index to use for client credentials must be set: [ENT_CRED_TLS_CONF](#AN_CMD_WSTAC_STORE_ID_ENT_CRED_TLS_CONF)

- If the client credential type is MSCHAPv2, the MSCHAPv2 username and password parameters must be set: [ENT_MSCHV2_UN](#AN_CMD_WSTAC_STORE_ID_ENT_MSCHV2_UN) and [ENT_MSCHV2_PW](#AN_CMD_WSTAC_STORE_ID_ENT_MSCHV2_PW)

Other WPA Enterprise credentials are optional, with default behaviours if they are not set:

- The WPA Enterprise tunnel method (TTLSv0, PEAPv0, PEAPv1, "none" or "any"; defaults to "any"): [ENT_TUNN_METHOD](#AN_CMD_WSTAC_STORE_ID_ENT_TUNN_METHOD)

> [!NOTE]
> TLS configurations must be configured using the [TLSC](#AN_MOD_TLS) module. In particular:
>
> - If the TLS configuration is to be used for client credentials, the client’s certificate and private key must be specified via [CERT_NAME](#AN_CMD_TLSC_STORE_ID_CERT_NAME) and [PRI_KEY_NAME](#AN_CMD_TLSC_STORE_ID_PRI_KEY_NAME)
>
> - For EAP-PEAPv0 tunnel method, TLS session caching is not supported and [SESSION_CACHING](#AN_CMD_TLSC_STORE_ID_SESSION_CACHING) is ignored
>
> - For TLS credential method, TLS session caching is not used and [SESSION_CACHING](#AN_CMD_TLSC_STORE_ID_SESSION_CACHING) is ignored
>
> - For WPA3 (and WPA2/WPA3 transition mode) Enterprise, server domain name verification must be enabled via [PEER_DOMAIN_VERIFY](#AN_CMD_TLSC_STORE_ID_PEER_DOMAIN_VERIFY) and [DOMAIN_NAME](#AN_CMD_TLSC_STORE_ID_DOMAIN_NAME)

> [!NOTE]
> For EAP-PEAP/TLS methods, it may be appropriate and convenient to use the same TLS configuration for both the tunnel method and the client credentials.

---
##### Example WPA Enterprise Configurations

###### Example 1: WPA3 Enterprise with MSCHAPv2 credentials

**First configure a TLS context for establishing a secure encrypted tunnel:**

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,1,"radius_cert"</strong></td>
<td>Specify file name of CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,6,"wifi.alpha.net"</strong></td>
<td>Specify authentication server’s domain name</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TIME_TIME">+TIME</a>=3</strong></td>
<td>Query to ensure time is valid (knowledge of current time is needed for TLS)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_TIME_TIME">+TIME</a>:"2025-10-24T18:03:43.00Z"</strong></td>
<td></td>
</tr>
</tbody>
</table>

Then configure the STA connection parameters, making use of the above TLS context:

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=1,"AUTO-WPA3-ENTERPRISE"</strong></td>
<td>Specify SSID of Access Point</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=2,9</strong></td>
<td>Set security type to WPA3-Enterprise</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=20,"<Anonymous@wifi.alpha.net>"</strong></td>
<td>Set Enterprise identity, to be sent unprotected (anonymous username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=21,"<my_username@wifi.alpha.net>"</strong></td>
<td>Set Enterprise identity, to be sent protected inside secure tunnel (real username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=26,1</strong></td>
<td>Set TLSC config index to use for establishing the tunnel</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=30,1</strong></td>
<td>Set credential type to MSCHAPv2</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=32,"my_username"</strong></td>
<td>Set MSCHAPv2 username</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=33,"my_password"</strong></td>
<td>Set MSCHAPv2 password</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Note that the tunnel method has not been specified here. Either EAP-TTLS or EAP-PEAP may be used, depending on the server’s request.

**Now connect:**

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NETIF_NETIFC">+NETIFC</a>=0,10,1</strong></td>
<td>Enable DHCP client</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>=1</strong></td>
<td>Start connection attempt</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTALU">+WSTALU</a>:1,"00:01:02:03:04:05",6</strong></td>
<td>Link up: connected on channel 6 to an AP with BSSID 00:01:02:03:04:05</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTAAIP">+WSTAAIP</a>:1,"192.168.0.20"</strong></td>
<td>IP address received via auto configuration (DHCP/SLAAC)</td>
</tr>
</tbody>
</table>

---
###### Example 2: WPA3 Enterprise with EAP-PEAPv1/TLS method

First configure a TLS context, including the user’s certificate and private key:

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,1,"radius_cert"</strong></td>
<td>Specify file name of CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,2,"my_cert"</strong></td>
<td>Specify file name of user’s certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,3,"my_key"</strong></td>
<td>Specify file name of user’s private key</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,6,"wifi.alpha.net"</strong></td>
<td>Specify authentication server’s domain name</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TIME_TIME">+TIME</a>=3</strong></td>
<td>Query to ensure time is valid (knowledge of current time is needed for TLS)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_TIME_TIME">+TIME</a>:"2025-10-24T18:03:43.00Z"</strong></td>
<td></td>
</tr>
</tbody>
</table>

Then configure the STA connection parameters, making use of the above TLS context for both establishing the tunnel and authenticating the client:

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=1,"AUTO-WPA3-ENTERPRISE"</strong></td>
<td>Specify SSID of Access Point</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=2,9</strong></td>
<td>Set security type to WPA3-Enterprise</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=20,"<Anonymous@wifi.alpha.net>"</strong></td>
<td>Set EAP identity to use during tunnel establishment (anonymous username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=21,"<my_username@wifi.alpha.net>"</strong></td>
<td>Set EAP identity to use inside secure tunnel (real username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=25,4</strong></td>
<td>Restrict tunnel method to PEAPv1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=26,2</strong></td>
<td>Set TLSC config index to use for establishing the tunnel</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=30,0</strong></td>
<td>Set credential type to TLS</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=31,2</strong></td>
<td>Set TLSC config index to use for authenticating the client</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

**Now connect:**

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NETIF_NETIFC">+NETIFC</a>=0,10,1</strong></td>
<td>Enable DHCP client</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>=1</strong></td>
<td>Start connection attempt</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTALU">+WSTALU</a>:1,"00:01:02:03:04:05",6</strong></td>
<td>Link up: connected on channel 6 to an AP with BSSID 00:01:02:03:04:05</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTAAIP">+WSTAAIP</a>:1,"192.168.0.20"</strong></td>
<td>IP address received via auto configuration (DHCP/SLAAC)</td>
</tr>
</tbody>
</table>

---
### Command Reference:

<a id="AN_CMD_AT_WSTA_WSTAC"></a>
#### +WSTAC

##### Description

This command is used to read or set the DCE’s Wi-Fi station mode configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WSTAC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WSTAC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WSTAC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response              | Description   |
|-----------------------|---------------|
| +WSTAC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_SSID"></span> 1</p></td>
<td style="text-align: left;"><p>&lt;SSID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Network name<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_SEC_TYPE"></span> 2</p></td>
<td style="text-align: left;"><p>&lt;SEC_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Security type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Open.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>WPA2-Personal Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>WPA2-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>WPA3-Personal Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>WPA3-Personal.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise Mixed Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>WPA2-Enterprise.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise Transition Mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>9</p></td>
<td style="text-align: left;"><p>WPA3-Enterprise.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_CREDENTIALS"></span> 3</p></td>
<td style="text-align: left;"><p>&lt;CREDENTIALS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Credentials for connecting to the network<br />
Maximum length of string is 128<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_CHANNEL"></span> 4</p></td>
<td style="text-align: left;"><p>&lt;CHANNEL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Current channel of BSS (or 0 for any)<br />
<br />
Valid range is 0 to 13<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_BSSID"></span> 5</p></td>
<td style="text-align: left;"><p>&lt;BSSID&gt;</p></td>
<td style="text-align: left;"><p>MAC Address<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of the network to connect to<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_CONN_TIMEOUT"></span> 7</p></td>
<td style="text-align: left;"><p>&lt;CONN_TIMEOUT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Connection timeout in milliseconds<br />
<br />
Valid range is 0 to 0x7FFFFFFF<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>&lt;NETIF_IDX&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Network interface index<br />
<br />
Valid range is 0 to 1<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ROAMING"></span> 9</p></td>
<td style="text-align: left;"><p>&lt;ROAMING&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Roaming state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Roaming is disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Roaming is enabled on WiFi only.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Roaming is enabled on layer 3.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_IDENT_PLAIN"></span> 20</p></td>
<td style="text-align: left;"><p>&lt;ENT_IDENT_PLAIN&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Identity for Enterprise, to be sent unprotected<br />
Maximum length of string is 255<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_IDENT_PROT"></span> 21</p></td>
<td style="text-align: left;"><p>&lt;ENT_IDENT_PROT&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Identity for Enterprise, to be sent protected (PEAP tunnels only)<br />
Maximum length of string is 255<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_TUNN_METHOD"></span> 25</p></td>
<td style="text-align: left;"><p>&lt;ENT_TUNN_METHOD&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Tunnel method for Enterprise<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Any.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>None.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>TTLSv0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>PEAPv0.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>PEAPv1.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_TUNN_TLS_CONF"></span> 26</p></td>
<td style="text-align: left;"><p>&lt;ENT_TUNN_TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC) to use for Enterprise tunnel<br />
<br />
Valid range is 0 to 4<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_CRED_TYPE"></span> 30</p></td>
<td style="text-align: left;"><p>&lt;ENT_CRED_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Type of credentials for Enterprise<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>TLS.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>MSCHAPv2.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_CRED_TLS_CONF"></span> 31</p></td>
<td style="text-align: left;"><p>&lt;ENT_CRED_TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC) to use for Enterprise TLS credentials<br />
<br />
Valid range is 0 to 4<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_MSCHV2_UN"></span> 32</p></td>
<td style="text-align: left;"><p>&lt;ENT_MSCHV2_UN&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Username element of Enterprise MSCHAPv2 credentials<br />
Maximum length of string is 255<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_ENT_MSCHV2_PW"></span> 33</p></td>
<td style="text-align: left;"><p>&lt;ENT_MSCHV2_PW&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Password element of Enterprise MSCHAPv2 credentials<br />
Maximum length of string is 255<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_MFP_TYPE"></span> 50</p></td>
<td style="text-align: left;"><p>&lt;MFP_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Management Frame Protection configuration<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>MFP Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>MFP Enabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>MFP Required.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_WSTAC_STORE_ID_WPA3_TD"></span> 51</p></td>
<td style="text-align: left;"><p>&lt;WPA3_TD&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>WPA3 Transition disable modifier<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>WPA3 Transition algorithms not modified.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>WPA3 Transition algorithms are disabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_WSTA_WSTA"></a>
#### +WSTA

##### Description

This command is used to control or query the DCE’s station mode functionality.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WSTA</p></td>
<td style="text-align: left;"><p>Read status of STA function<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WSTA=&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Set state of STA function<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>State of the Wi-Fi station feature<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Use configuration from +WSTAC.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response                     | Description |
|------------------------------|-------------|
| +WSTA:\<ASSOC_ID\>,\<STATE\> | State       |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Connected state<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Not connected.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
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
#### +WSTAAIP

##### Description

**Indication of STA automatic address assignment.**

| AEC | Description |
|----|----|
| +WSTAAIP:\<ASSOC_ID\>,\<IP_ADDRESS\> | Assignment of IP address to association |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;IP_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>IP address assigned<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_WSTA_WSTALD"></a>
#### +WSTALD

##### Description

**Link lost.**

| AEC                  | Description |
|----------------------|-------------|
| +WSTALD:\<ASSOC_ID\> | Link down   |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +WSTAERR

##### Description

**Connection error.**

| AEC                     | Description |
|-------------------------|-------------|
| +WSTAERR:\<ERROR_CODE\> | Link error  |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_WSTA_WSTALU"></a>
#### +WSTALU

##### Description

**Link established.**

| AEC                                        | Description |
|--------------------------------------------|-------------|
| +WSTALU:\<ASSOC_ID\>,\<BSSID\>,\<CHANNEL\> | Link up     |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BSSID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of the Access Point the DCE has connected to<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CHANNEL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The channel number of network<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_WSTA_WSTAROAM"></a>
#### +WSTAROAM

##### Description

**Roaming occurred.**

| AEC                    | Description      |
|------------------------|------------------|
| +WSTAROAM:\<ASSOC_ID\> | Roaming occurred |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

WPA Personal: Configure STA connection parameters
<a id="EXAMPLE_WSTA_PERSONAL"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=1,"MyAP"</strong></td>
<td>Specify SSID of Access Point</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=2,3</strong></td>
<td>Set security type to WPA2-Personal</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=3,"MyAPPSK"</strong></td>
<td>Set WPA2 Personal passphrase for connecting to the Access Point</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Connect at Wi-Fi and IP layers
<a id="EXAMPLE_WSTA_CONNECT"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NETIF_NETIFC">+NETIFC</a>=0,10,1</strong></td>
<td>Enable DHCP client</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>=1</strong></td>
<td>Start connection attempt</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTALU">+WSTALU</a>:1,"00:01:02:03:04:05",6</strong></td>
<td>Link up: connected on channel 6 to an AP with BSSID 00:01:02:03:04:05</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTAAIP">+WSTAAIP</a>:1,"192.168.0.20"</strong></td>
<td>IP address received via auto configuration (DHCP/SLAAC)</td>
</tr>
</tbody>
</table>

Some disconnections, reconnections and roaming
<a id="EXAMPLE_WSTA_RECONNECT"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>=1</strong></td>
<td>Start connection attempt</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTALU">+WSTALU</a>:1,"00:01:02:03:04:05",11</strong></td>
<td>Link up: connected on channel 11</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTAAIP">+WSTAAIP</a>:1,"192.168.0.20"</strong></td>
<td>IP address received via auto configuration (DHCP/SLAAC)</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>=0</strong></td>
<td>Disconnect</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a></strong></td>
<td>Query STA status</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>:0</strong></td>
<td>STA is not connected</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>=1</strong></td>
<td>Start connection attempt</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTALU">+WSTALU</a>:1,"00:01:02:03:04:05",11</strong></td>
<td>Link up: connected on channel 11</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTAAIP">+WSTAAIP</a>:1,"192.168.0.20"</strong></td>
<td>IP address received via auto configuration (DHCP/SLAAC)</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTAROAM">+WSTAROAM</a>:1</strong></td>
<td>STA has roamed</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTAAIP">+WSTAAIP</a>:1,"10.1.0.5"</strong></td>
<td>Change in IP address due to layer 3 roaming</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a></strong></td>
<td>Query STA status</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WSTA_WSTA">+WSTA</a>:1</strong></td>
<td>STA is connected</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_WSTA_WSTALD">+WSTALD</a></strong></td>
<td>Link down</td>
</tr>
</tbody>
</table>

WPA Enterprise: Configure a TLS context for establishing a tunnel
<a id="EXAMPLE_WSTA_ENTERPRISE_TUNNEL"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,1,"radius_cert"</strong></td>
<td>Specify file name of CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,6,"wifi.alpha.net"</strong></td>
<td>Specify authentication server’s domain name</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TIME_TIME">+TIME</a>=3</strong></td>
<td>Query to ensure time is valid (knowledge of current time is needed for TLS)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_TIME_TIME">+TIME</a>:"2025-10-24T18:03:43.00Z"</strong></td>
<td></td>
</tr>
</tbody>
</table>

WPA Enterprise: Configure STA connection parameters for MSCHAPv2
<a id="EXAMPLE_WSTA_ENTERPRISE_MSCHAPV2"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=1,"AUTO-WPA3-ENTERPRISE"</strong></td>
<td>Specify SSID of Access Point</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=2,9</strong></td>
<td>Set security type to WPA3-Enterprise</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=20,"<Anonymous@wifi.alpha.net>"</strong></td>
<td>Set Enterprise identity, to be sent unprotected (anonymous username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=21,"<my_username@wifi.alpha.net>"</strong></td>
<td>Set Enterprise identity, to be sent protected inside secure tunnel (real username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=26,1</strong></td>
<td>Set TLSC config index to use for establishing the tunnel</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=30,1</strong></td>
<td>Set credential type to MSCHAPv2</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=32,"my_username"</strong></td>
<td>Set MSCHAPv2 username</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=33,"my_password"</strong></td>
<td>Set MSCHAPv2 password</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

WPA Enterprise: Configure a TLS context for EAP-PEAPv1/TLS
<a id="EXAMPLE_WSTA_ENTERPRISE_TLS_TLSC"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,1,"radius_cert"</strong></td>
<td>Specify file name of CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,2,"my_cert"</strong></td>
<td>Specify file name of user’s certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,3,"my_key"</strong></td>
<td>Specify file name of user’s private key</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,6,"wifi.alpha.net"</strong></td>
<td>Specify authentication server’s domain name</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TIME_TIME">+TIME</a>=3</strong></td>
<td>Query to ensure time is valid (knowledge of current time is needed for TLS)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_TIME_TIME">+TIME</a>:"2025-10-24T18:03:43.00Z"</strong></td>
<td></td>
</tr>
</tbody>
</table>

WPA Enterprise: Configure STA connection parameters for EAP-PEAPv1/TLS
<a id="EXAMPLE_WSTA_ENTERPRISE_TLS_WSTAC"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=1,"AUTO-WPA3-ENTERPRISE"</strong></td>
<td>Specify SSID of Access Point</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=2,9</strong></td>
<td>Set security type to WPA3-Enterprise</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=20,"<Anonymous@wifi.alpha.net>"</strong></td>
<td>Set EAP identity to use during tunnel establishment (anonymous username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=21,"<my_username@wifi.alpha.net>"</strong></td>
<td>Set EAP identity to use inside secure tunnel (real username)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=25,4</strong></td>
<td>Restrict tunnel method to PEAPv1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=26,2</strong></td>
<td>Set TLSC config index to use for establishing the tunnel</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=30,0</strong></td>
<td>Set credential type to TLS</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WSTA_WSTAC">+WSTAC</a>=31,2</strong></td>
<td>Set TLSC config index to use for authenticating the client</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_ASSOC"></a>
## ASSOC (Module ID = 22)

### Command Reference:

#### +ASSOC

##### Description

This command is used to query current WiFi associations.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+ASSOC</p></td>
<td style="text-align: left;"><p>Query all associations<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+ASSOC=&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>Query specific association ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ASSOC_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +ASSOC

##### Description

**WiFi association report.**

| AEC                                               | Description             |
|---------------------------------------------------|-------------------------|
| +ASSOC:\<ASSOC_ID\>,\<AP_STA\>,\<BSSID\>,\<RSSI\> | WiFi association report |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Association ID<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;AP_STA&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>AP or STA<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>AP.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>STA.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;BSSID&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>The BSSID of association peer<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSSI&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>RSSI<br />
</p></td>
</tr>
</tbody>
</table>

---
## SI (Module ID = 23)

### Command Reference:

#### +SI

##### Description

This command is used to query system information.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SI</p></td>
<td style="text-align: left;"><p>Request system information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SI=&lt;FILTER&gt;</p></td>
<td style="text-align: left;"><p>Request filtered system information<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;FILTER&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>System information filter bitmask<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0x01</p></td>
<td style="text-align: left;"><p>WiFi memory allocation stats.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x02</p></td>
<td style="text-align: left;"><p>WiFi packet stats.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x04</p></td>
<td style="text-align: left;"><p>Heap allocation stats.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>0x08</p></td>
<td style="text-align: left;"><p>Stack usage stats.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response       | Description |
|----------------|-------------|
| +SI:\<UPTIME\> | Response    |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>System uptime in seconds<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +SIMSTAT

##### Description

**WiFi memory statistics for each type of memory pool.**

| AEC | Description |
|----|----|
| +SIMSTAT:\<TYPE\>,\<ALLOC\>,\<FREE\>,\<ALLOC_SZ\>,\<FREE_SZ\> | WiFi memory statistic |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Memory.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Config.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>High priority TX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>High priority RX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Normal priority TX.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>Normal priority RX.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of memory allocations made<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of memory frees<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC_SZ&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Total bytes allocated<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_SZ&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Total bytes freed<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SIMERR

##### Description

**WiFi Memory errors.**

| AEC                   | Description        |
|-----------------------|--------------------|
| +SIMERR:\<ALLOC_ERR\> | WiFi memory errors |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Memory allocation errors<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SIWPKTS

##### Description

**WiFi packets statistics.**

| AEC                    | Description  |
|------------------------|--------------|
| +SIWPKTS:\<TX\>,\<RX\> | WiFi packets |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>WiFi packets transmitted<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RX&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>WiFi packets received<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SIHEAP

##### Description

**Heap allocation statistics.**

| AEC | Description |
|----|----|
| +SIHEAP:\<ALLOC\>,\<FREE\>,\<ALLOC_SZ\>,\<FREE_SZ\>,\<PEAK_ALLOC_SZ\> | Heap statistics |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of memory allocations made<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of memory frees<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ALLOC_SZ&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Total bytes allocated<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FREE_SZ&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Total bytes freed<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEAK_ALLOC_SZ&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Peak bytes allocated<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SIHERR

##### Description

**Heap allocation errors.**

| AEC                   | Description |
|-----------------------|-------------|
| +SIHERR:\<ALLOC_ERR\> | Heap errors |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Memory allocation errors<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +SISTACK

##### Description

**Stack usage.**

| AEC | Description |
|----|----|
| +SISTACK:\<STACK_MIN_RESERVED\>,\<STACK_RESERVED\>,\<STACK_USAGE\> | Stack statistics |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Minimum stack reserved memory<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;STACK_RESERVED&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Stack reserved memory<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;STACK_USAGE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Stack usage<br />
</p></td>
</tr>
</tbody>
</table>

---
## WPROV (Module ID = 25)

### Command Reference:

#### +WPROVC

##### Description

This command is used to read or set the provisioning service configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WPROVC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WPROVC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WPROVC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response               | Description   |
|------------------------|---------------|
| +WPROVC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;PORT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Service listening port<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;ASCII&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>ASCII or binary protocol<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Binary protocol.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ASCII protocol.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;PROTOCOL_VERSION&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>IP protocol version<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>IPv4.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>IPv6.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
#### +WPROV

##### Description

This command is used to control or query the provisioning service.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WPROV</p></td>
<td style="text-align: left;"><p>Read status of provisioning service<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WPROV=&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Set state of provisioning service<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>State of the provisioning service<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Use configuration from +WPROVC.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +WPROVAT

##### Description

**Indication of client attach to provisioning service.**

| AEC | Description |
|----|----|
| +WPROVAT:\<ID\>,\<IP_ADDRESS\>,\<PORT\> | Attachment of client to provisioning service |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Client ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;IP_ADDRESS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>IP address assigned<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PORT&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Port<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +WPROVDT

##### Description

**Indication of client detach from provisioning service.**

| AEC             | Description                                    |
|-----------------|------------------------------------------------|
| +WPROVDT:\<ID\> | Detachment of client from provisioning service |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Client ID<br />
</p></td>
</tr>
</tbody>
</table>

---
## DI (Module ID = 26)

### Introduction:

#### Firmware image sequence numbers

Contained within each [IMAGE_INFO](#AN_CMD_DI_STORE_ID_IMAGE_INFO) is a `SEQ_NUM` value, this represents the image sequence number. The boot process prefers the image with the lower sequence number.

> [!NOTE]
> >
> **The following sequence numbers are invalid:**
>
> - 0
>
> - 0xFFFFFFFF
>
> 
---
### Command Reference:

<a id="AN_CMD_AT_DI_DI"></a>
#### +DI

##### Description

This command is used to query the device information.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+DI</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+DI=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
</tbody>
</table>

| Response           | Description   |
|--------------------|---------------|
| +DI:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;DEVICE_ID&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Device ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>&lt;NUM_IMAGES&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Number of images<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_DI_STORE_ID_IMAGE_INFO"></span> 15</p></td>
<td style="text-align: left;"><p>&lt;IMAGE_INFO&gt;</p></td>
<td style="text-align: left;"><p>Complex Value<sup>1</sup><br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Image information<br />
This is a multiple value parameter<br />
with an ID range 15.0 to 15.1<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
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
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>The image has not yet been activated.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>The image will run on next boot (subject to verification).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>The image is currently running.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
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

Query device information with [+DI](#AN_CMD_AT_DI_DI)
<a id="EXAMPLE_b24cb7601966bd304010fa7449e5f57c0507b958"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DI_DI">+DI</a></strong></td>
<td>Query all device information</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DI_DI">+DI</a>:1,0x29C70053</strong></td>
<td>Device ID</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DI_DI">+DI</a>:14,2</strong></td>
<td>2 images</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DI_DI">+DI</a>:15.0,0xFFEEDDC0,0x00010200,0x60000000,2</strong></td>
<td>Image info for currently running image</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DI_DI">+DI</a>:15.1,0xFFFFFFFF,0x00010300,0xFFFFFFFF,0</strong></td>
<td>Image info for latent image</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_EXTCRYPTO"></a>
## EXTCRYPTO (Module ID = 27)

### Introduction

Cryptographic operations can be delegated to an external crypto device, providing secure key storage and hardware-accelerated public key operations. The user can choose the on-module ATECC608A-TNGTLS or equivalent third-party device.

The ATECC608A-TNGTLS is the Trust-and-Go pre-provisioned variant of the ATECC608, featuring ECDSA signing, ECC Private Key secure storage, and X.509 compressed certificate storage. Access to the on-module secure element is made through a separate I2C or SWI interface.

The [+EXTCRYPTO](#AN_AEC_AT_EXTCRYPTO_EXTCRYPTO) AEC allows the DTE to receive a crypto operation request from the DCE. The [+EXTCRYPTO](#AN_CMD_AT_EXTCRYPTO_EXTCRYPTO) command is used to send the operation result back to the DCE.

Crypto operation requests are enabled via the [EXTCRYPTO_OPS](#AN_CMD_TLSC_STORE_ID_EXTCRYPTO_OPS) parameter of the [+TLSC](#AN_CMD_AT_TLS_TLSC) command. The only supported operation is ECDSA signing.

#### Using External Crypto for Secure Signing

To leverage the crypto device for secure signing, the application should follow these steps:

1.  Retrieve from the crypto device the X.509 certificate that includes the public key corresponding to the securely stored private key.

2.  Send the X.509 certificate to the DCE using the [+FS](#AN_CMD_AT_FS_FLFS_FS) command.

3.  Enable secure signing via the external crypto device and specify the certificate in the TLS configuration.

    See example [configuring TLS with external crypto](#EXAMPLE_EXTCRYPTO_TLS).

4.  Respond to signing requests from the [+EXTCRYPTO](#AN_AEC_AT_EXTCRYPTO_EXTCRYPTO) AEC with the [+EXTCRYPTO](#AN_CMD_AT_EXTCRYPTO_EXTCRYPTO) command.

    See example [handling signing request and sending response](#EXAMPLE_EXTCRYPTO).

> [!NOTE]
> The ECC curve used for signing is selected according to the certificate public key. Refer to the CURVE element in the [+EXTCRYPTO](#AN_AEC_AT_EXTCRYPTO_EXTCRYPTO) AEC for the list of supported curves.

> [!NOTE]
> The application code is responsible for interacting with the external crypto device to retrieve the certificate and forward signing requests and responses.

---
### Command Reference:

<a id="AN_CMD_AT_EXTCRYPTO_EXTCRYPTO"></a>
#### +EXTCRYPTO

##### Description

This command is used to provide the result of an external crypto operation.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+EXTCRYPTO=&lt;OP_ID&gt;,&lt;STATUS&gt;</p></td>
<td style="text-align: left;"><p>Provide the result of a failed external signing operation<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+EXTCRYPTO=&lt;OP_ID&gt;,&lt;STATUS&gt;,&lt;SIGNATURE&gt;</p></td>
<td style="text-align: left;"><p>Provide the result of a successful external signing operation<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OP_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation identifier, matching &lt;OP_ID&gt; in corresponding AEC<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;STATUS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation success or failure<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Operation succeeded.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Operation failed.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGNATURE&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Signature (big endian). For ECDSA signatures: R then S, each the size of the curve.<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_EXTCRYPTO_EXTCRYPTO"></a>
#### +EXTCRYPTO

##### Description

**This event is used to request an external crypto operation.**

| AEC | Description |
|----|----|
| +EXTCRYPTO:\<OP_ID\>,\<OP_TYPE\>,\<OP_SOURCE_TYPE\>,\<OP_SOURCE_ID\>,\<SIGN_TYPE\>,\<CURVE\>,\<SIGN_VALUE\> | Request an external signing operation |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Operation identifier, to be included in EXTCRYPTO CMD<br />
<br />
Positive unsigned 16-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OP_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The type of operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Signing.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OP_SOURCE_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The type of source requesting the operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>A TLSC configuration.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;OP_SOURCE_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The ID of the source requesting the operation<br />
<br />
Valid range is 1 to 2<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGN_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The type of signing operation<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>ECDSA.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CURVE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The ECDSA curve<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Curve secp256r1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Curve secp384r1.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Curve secp521r1.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SIGN_VALUE&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>The value to be signed (big endian)<br />
</p></td>
</tr>
</tbody>
</table>

---
### Examples:

Example of TLS configuration for secure signing via external crypto operations
<a id="EXAMPLE_EXTCRYPTO_TLS"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,41,1</strong></td>
<td>Enable server domain verification</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,6,"ServerDomain"</strong></td>
<td>Specify server domain name</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,40,1</strong></td>
<td>Enable server authentication</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,1,"ServerRootCACert"</strong></td>
<td>Specify file name of CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,2,"EccClientCert"</strong></td>
<td>Specify file name of ECC client certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=2,20,1</strong></td>
<td>Enable signing via external crypto</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

Example of signing request/response using [+EXTCRYPTO](#AN_CMD_AT_EXTCRYPTO_EXTCRYPTO)
<a id="EXAMPLE_EXTCRYPTO"></a>

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_EXTCRYPTO_EXTCRYPTO">+EXTCRYPTO</a>:123,1,1,2,1,1,\[0123…​cdef\]</strong></td>
<td>Crypto request ID 123: ECDSA signing using curve secp256r1, for TLS config 2</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_EXTCRYPTO_EXTCRYPTO">+EXTCRYPTO</a>=123,0,\[0123…​cdef\]</strong></td>
<td>Response to crypto request ID 123</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
## WIFI (Module ID = 28)

### Command Reference:

<a id="AN_CMD_AT_WIFI_WIFIC"></a>
#### +WIFIC

##### Description

This command is used to read or set the device’s Wi-Fi configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+WIFIC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WIFIC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+WIFIC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response              | Description   |
|-----------------------|---------------|
| +WIFIC:\<ID\>,\<VAL\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;REGDOMAIN_SELECTED&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Regulatory domain selected<br />
Maximum length of string is 6<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>&lt;REGDOMAIN_AVAILABLE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Regulatory domains available<br />
Maximum length of string is 6<br />
This is a multiple value parameter<br />
with an ID range 11.0 to 11.5<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>&lt;REGDOMAIN_CHANMASK24&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
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
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>&lt;POWERSAVE&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Power Save Mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>On.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>&lt;POWERSAVE_LISTEN_INTERVAL&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Listen Interval in units of beacon period<br />
<br />
Valid range is 3 to 100<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>&lt;POWERSAVE_INACT_LIMIT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Inactivity Time Limit - the sleep inactivity threshold/limit for power-save operation in seconds<br />
<br />
Valid range is 10 to 6000<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>30</p></td>
<td style="text-align: left;"><p>&lt;COEX_ENABLED&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>31</p></td>
<td style="text-align: left;"><p>&lt;COEX_INTERFACE_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter interface type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>3-wire interface (BT_Act, BT_Prio, WLAN_Act).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>2-wire interface (BT_Prio, WLAN_Act).</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>32</p></td>
<td style="text-align: left;"><p>&lt;COEX_WLAN_RX_VS_BT&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter WLAN Rx priority over BT Low Priority<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>WLAN Rx priority lower than BT Low Priority.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>WLAN Rx priority higher than BT Low Priority.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>33</p></td>
<td style="text-align: left;"><p>&lt;COEX_WLAN_TX_VS_BT&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter WLAN Tx priority over BT Low Priority<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>WLAN Tx priority lower than BT Low Priority.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>WLAN Tx priority higher than BT Low Priority.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>34</p></td>
<td style="text-align: left;"><p>&lt;COEX_ANTENNA_MODE&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>BT/Wi-Fi coexistence arbiter antenna mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Dedicated antenna.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Shared antenna.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>&lt;AMPDU_TX_ENABLED&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Wi-Fi A-MPDU Tx Enable<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
---
### Examples:

Settings with [+WIFIC](#AN_CMD_AT_WIFI_WIFIC)
<a id="EXAMPLE_83aadd2a5891271329d9dc62f4cea81d34571a9e"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=10,"USA"</strong></td>
<td>Configure regulatory domain to USA</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=10,"JPN"</strong></td>
<td>Configure regulatory domain to JPN</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=10</strong></td>
<td>Query regulatory domain</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>:10,"JPN"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=20</strong></td>
<td>Query power save mode</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>:20,0</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=20,1</strong></td>
<td>Configure power save on</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

[+WIFIC](#AN_CMD_AT_WIFI_WIFIC) coexistence settings for 3-wire PTA interface
<a id="EXAMPLE_c37bae967b299185b054858a003c7507e0b388a9"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=31,0</strong></td>
<td>Configure 3-wire interface</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=32,1</strong></td>
<td>WLAN RX priority higher than BT low priority</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=33,1</strong></td>
<td>WLAN TX priority higher than BT low priority</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=34,1</strong></td>
<td>Shared antenna</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=30,1</strong></td>
<td>Enable coex</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_NVM"></a>
## NVM (Module ID = 29)

### Command Reference:

<a id="AN_CMD_AT_NVM_NVMC"></a>
#### +NVMC

##### Description

This command is used to read or set the NVM configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+NVMC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+NVMC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+NVMC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;START_OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Starting address offset<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;NUM_SECTORS&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Number of sectors<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;SECTOR_SZ&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Sector size<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;CHECK_MODE&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Checking mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>CRC16.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_NVM_NVMER"></a>
#### +NVMER

##### Description

This command allows sector erase within the alternate firmware partition.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+NVMER=&lt;SECTOR_OFFSET&gt;,&lt;SECTORS&gt;</p></td>
<td style="text-align: left;"><p>NVM erase sectors<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;SECTOR_OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Sector offset to be used for the NVM operation<br />
<br />
Valid range is 0 to 239<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;SECTORS&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of sectors to erase during NVM operation<br />
<br />
Valid range is 1 to 240<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_NVM_NVMWR"></a>
#### +NVMWR

##### Description

This command allows data to be written to the alternate firmware partition. Writes are performed as normal for flash devices, therefore it is recommended to erase the sector of data before performing a write. Write operations cannot cross a sector boundary.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+NVMWR=&lt;OFFSET&gt;,&lt;LENGTH&gt;,&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>NVM write with offset, length and data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Byte offset to be used for the NVM operation<br />
<br />
Valid range is 0 to 0x000EFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes for the NVM operation<br />
<br />
Valid range is 1 to 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>The data to write in hexadecimal string format<br />
<br />
Valid range is 1 to 1024<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_NVM_NVMCHK"></a>
#### +NVMCHK

##### Description

This command allows checking of the alternate firmware partition.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+NVMCHK=&lt;OFFSET&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>NVM check<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Byte offset to be used for the NVM operation<br />
<br />
Valid range is 0 to 0x000EFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes for the NVM operation<br />
<br />
Valid range is 1 to 0x000F0000<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_NVM_NVMRD"></a>
#### +NVMRD

##### Description

This command allows reading of the alternate firmware partition.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+NVMRD=&lt;OFFSET&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>NVM read<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Byte offset to be used for the NVM operation<br />
<br />
Valid range is 0 to 0x000EFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes for the NVM operation<br />
<br />
Valid range is 1 to 1024<br />
</p></td>
</tr>
</tbody>
</table>

| Response                              | Description   |
|---------------------------------------|---------------|
| +NVMRD:\<OFFSET\>,\<LENGTH\>,\<DATA\> | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Byte offset<br />
<br />
Valid range is 0 to 0x000EFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes<br />
<br />
Valid range is 1 to 1024<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Byte Array<br />
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

#### +NVMER

##### Description

**NVM Erase.**

| AEC    | Description       |
|--------|-------------------|
| +NVMER | NVM erase success |

AEC Syntax

---
<a id="AN_AEC_AT_NVM_NVMCHK"></a>
#### +NVMCHK

##### Description

**NVM Check.**

| AEC                                                   | Description   |
|-------------------------------------------------------|---------------|
| +NVMCHK:\<OFFSET\>,\<LENGTH\>,\<CHECK_MODE\>,\<HASH\> | Hash response |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Byte offset<br />
<br />
Valid range is 0 to 0x000EFFFF<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The number of bytes<br />
<br />
Valid range is 1 to 0x000F0000<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;CHECK_MODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Checking mode used<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>CRC16.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;HASH&gt;</p></td>
<td style="text-align: left;"><p>String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Hash response<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +NVMERR

##### Description

**NVM error.**

| AEC                    | Description |
|------------------------|-------------|
| +NVMERR:\<ERROR_CODE\> | NVM error   |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

Simple example of NVM usage
<a id="EXAMPLE_NVM_EXAMPLE"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMER">+NVMER</a>=0,1</strong></td>
<td>Erase first sector</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_NVM_NVMER">+NVMER</a></strong></td>
<td>Erase complete AEC</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMWR">+NVMWR</a>=0,4,\[4D434850\]</strong></td>
<td>Write 4 bytes of data to offset 0</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMCHK">+NVMCHK</a>=0,4</strong></td>
<td>Request CRC16 checksum, 4 bytes from offset 0</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_NVM_NVMCHK">+NVMCHK</a>:0x00000000,4,2,0xCD77</strong></td>
<td>CRC16 checksum AEC</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMC">+NVMC</a>=4,11</strong></td>
<td>Set check mode to SHA256</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMCHK">+NVMCHK</a>=0,4</strong></td>
<td>Request SHA256 hash, 4 bytes from offset 0</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_NVM_NVMCHK">+NVMCHK</a>:0x00000000,4,11,\[7BE8FA11F537A1CA4612D6E30CAF94A20F3C37999012119672BE21DAD2791D5C\]</strong></td>
<td>SHA256 AEC</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_NVM_NVMRD">+NVMRD</a>=0,4</strong></td>
<td>Read 4 bytes of data from offset 0</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_NVM_NVMRD">+NVMRD</a>:0x00000000,4,"MCHP"</strong></td>
<td>Read data response</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_DFU"></a>
## DFU (Module ID = 30)

### Introduction

Secure Device Firmware Update (DFU) is a process for upgrading the firmware of a secured device.

The RNWF02 device has non-volatile memory (NVM) with two partitions which may be used to store firmware images.

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

Locate the released RNWF02.bootable.dfu file for the firmware version to which you want to upgrade.

Read the firmware image from the file, then update two values:

- Sequence Number: The Sequence Number is the boot priority of the firmware image. Use the [+DFUSEQ](#AN_CMD_AT_DFU_DFUSEQ) command to get the offset, length and value for updating it.

- Firmware Image Source Address: The Firmware Image Source Address must match the physical address of the NVM partition in which the firmware image is to be programmed. Use the [+DFUADR](#AN_CMD_AT_DFU_DFUADR) command, with the desired partition, to get the offset, length and value for updating it.

> [!NOTE]
> A status code of [DFU_ADDRESS_WARNING](#AN_STATUS_DFU_ADDRESS_WARNING) is a warning that the other partition does not contain a bootable firmware image. If the user proceeds in spite of this warning and step 4 does not complete for any reason, the device will reach a state in which it contains no bootable firmware images. In that situation, repeating step 4 should recover the device, so long as the user still has the firmware image available.

> [!NOTE]
> Save the value of the NVM partition address for use during step 4.

#### 3. Boot the device in DFU mode

Boot the device in DFU mode using the following steps:

1.  Assert RNWF02 pin NMCLR (low).

2.  Write to RNWF02 pins PB0 (Clock) and PB1 (Data) to send the DFU Test Mode Entry pattern "MCHP".

3.  Deassert RNWF02 pin NMCLR.

#### 4. Erase and program the NVM partition

Configure pins PB0 and PB1 for UART Rx and Tx respectively.

Use Programming Executive (PE) commands to erase the NVM partition, at the address obtained during step 2.

Use Programming Executive (PE) commands to program the new firmware image into the NVM partition, at the address obtained during step 2.

---
### Command Reference:

<a id="AN_CMD_AT_DFU_DFUADR"></a>
#### +DFUADR

##### Description

This command is used to get the parameters for modifying the little endian address field of a DFU image.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+DFUADR=&lt;PARTITION&gt;</p></td>
<td style="text-align: left;"><p>Get parameters appropriate for the specified partition<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;PARTITION&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The partition into which the DFU image will be programmed<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Alternate partition (recommended).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Current partition.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Low partition.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>High partition.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +DFUADR:\<OFFSET\>,\<LENGTH\>,\<VALUE\> | Parameters for modifying the little endian address field of a DFU image |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Offset (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALUE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Value to write to field in DFU image<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_DFU_DFUSEQ"></a>
#### +DFUSEQ

##### Description

This command is used to get the parameters for modifying the little endian sequence number field of a DFU image.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+DFUSEQ=&lt;IMAGE_STATE&gt;</p></td>
<td style="text-align: left;"><p>Get parameters appropriate for the specified image state<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;IMAGE_STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The desired state of the DFU image after programming<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Latent image (will not run until activated).</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Activated image.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +DFUSEQ:\<OFFSET\>,\<LENGTH\>,\<VALUE\> | Parameters for modifying the little endian sequence number field of a DFU image |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Offset (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length (in bytes) of field in DFU image<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VALUE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Value to write to field in DFU image<br />
</p></td>
</tr>
</tbody>
</table>

---
---
### Examples:

Example of using [+DFUADR](#AN_CMD_AT_DFU_DFUADR) and [+DFUSEQ](#AN_CMD_AT_DFU_DFUSEQ)
<a id="EXAMPLE_154f5dd58fe255da7480e1634642e778c98de910"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DFU_DFUADR">+DFUADR</a>=0</strong></td>
<td>Get parameters for making an image for the alternate partition</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DFU_DFUADR">+DFUADR</a>:20,4,0x600F0000</strong></td>
<td>Offset 20, length 4, value 0x600F0000</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td></td>
<td><code>**</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DFU_DFUADR">+DFUADR</a>=1</strong></td>
<td>Get parameters for making an image for the current partition</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DFU_DFUADR">+DFUADR</a>:20,4,0x60000000</strong></td>
<td>Offset 20, length 4, value 0x60000000</td>
</tr>
<tr>
<td>←</td>
<td><code>ERROR:30.0,"No Bootable Image In Other Partition"</code></td>
<td></td>
</tr>
<tr>
<td></td>
<td><code>**</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DFU_DFUSEQ">+DFUSEQ</a>=0</strong></td>
<td>Get parameters for making an activated image</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DFU_DFUSEQ">+DFUSEQ</a>:0,4,0xFFEEDDC0</strong></td>
<td>Offset 0, length 4, value 0xFFEEDDC0</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td></td>
<td><code>**</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_DFU_DFUSEQ">+DFUSEQ</a>=1</strong></td>
<td>Get parameters for making a latent image</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_DFU_DFUSEQ">+DFUSEQ</a>:0,4,0xFFFFFFFF</strong></td>
<td>Offset 0, length 4, value 0xFFFFFFFF</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_PPS"></a>
## PPS (Module ID = 31)

### Introduction

The RNWF02 device supports two advanced power-saving modes designed to reduce current consumption in typical IoT and embedded applications:

- **Platform Power-Save (PPS)** mode places the CPU and hardware peripherals into sleep modes - most clocks and peripherals are powered down, leaving only essential hardware blocks active. This drastically reduces power consumption while preserving Wi-Fi connectivity and system context, enabling rapid wake-up and seamless operation.

- **EXtreme Deep Sleep (XDS)** enters the device’s lowest power state, with all peripherals powered down and system context lost. This mode achieves maximum power savings for long standby periods where Wi-Fi or network connections are not required. Waking from XDS triggers a full system reboot.

#### PPS Operation Details

When **PPS** is enabled, the system automatically transitions into PPS mode during idle periods, minimising power while maintaining system and Wi-Fi state. This includes active protocol connections, Wi-Fi association, and buffered data queues.

##### Wake-Up Triggers

There are a number of events that will cause the RNWF02 to wake when PPS is active:

- Internal timers or internal scheduled events

  - These will be accounted for when PPS calculates its sleep duration for the next period, ensuring it wakes up in time to process the next event/timer

- Host Data Terminal Equipment (DTE) activity over the UART

  - The UART wake protocol (see [Wake-up Via Uart](#_wake_up_via_uart)) will wake the RNWF02 immediately

- In the absence of internal timers or external triggers, PPS will wake the RNWF02 after 10 seconds

Once awake, the RNWF02 will run until the next idle period, whereby it will transition into PPS mode again.

##### Wi-Fi Power Save Mode during PPS

When PPS is enabled and Wi-Fi is connected, the RNWF02 operates Wi-Fi Legacy Powersave to minimise power consumption while maintaining network connectivity.

###### Listen Interval

The RNWF02 wakes periodically based on the configured Wi-Fi Listen Interval, which determines how often it wakes to listen for buffered traffic from the AP. By default, this interval is 10 beacon periods, roughly equivalent to 1 second (typical beacon interval is 102.4 ms).

###### DTIM (Delivery Traffic Indication Message) Awareness

To efficiently receive broadcast and multicast traffic buffered by the AP, the device aims to wake on the closest DTIM period aligned with the configured listen interval. The DTIM is a special beacon that signals buffered broadcast/multicast data transmission by the AP. For example, if the Listen Interval is set to 10 beacon periods (default) and the AP’s DTIM period is 3, the RNWF02 will wake after 9 beacon periods (i.e. on the 3rd DTIM) instead of exactly after 10 beacons. This alignment maximises power savings by minimising unnecessary wake events while ensuring timely reception of important broadcast traffic.

##### Sleep Timing Accuracy

To optimise power saving and accuracy of wake intervals, it is strongly recommended to connect and enable a secondary oscillator (SOSC) clocked at 32768 Khz. The SOSC provides a high-accuracy timing source during sleep, allowing for more precise wake-up timing when using longer sleep durations.

##### PPS Pause

PPS Pause allows temporarily suspending Platform Power-Save operation without fully disabling it. This is useful during periods where continuous device responsiveness is required, such as during critical command sequences, firmware updates or other high-activity times when entering sleep state would be undesirable.

###### How PPS Pause Works

- When a pause is active, the system remains fully awake, bypassing PPS sleep transitions.

- Multiple pause commands can be issued sequentially, and the pause durations extend the total pause period.

- After all active pause timers expire, the RNWF02 automatically sends an Automatic Event Callback (AEC) for informational purposes, to indicate that PPS will now resume.

- Once the pause period has expired, the system will return to normal PPS operation, entering low-power sleep during idle periods.

<a id="_wake_up_via_uart"></a>
##### Wake-Up via UART

- The RNWF02 UART interface uses the dedicated flow control pins to wake the device:

  - **WAKE_REQ (PB2):** The host DTE asserts a **rising edge** on this pin to request RNWF02 to wake from PPS sleep.

  - **WAKE_RDY (PA4):** The RNWF02 responds by pulling this pin **active-low** once it is ready to receive AT commands.

> [!NOTE]
> - RTS/CTS hardware flow control is **not supported** under PPS operation on RNWF02
>
> - Wake-up latency from PPS mode is approximately **4 ms**.

##### Timed Wake-Up

In the case that an RNWF02 user doesn’t have the dedicated flow control pins PB2/PB4 wired to wake the device, it is possible to set a fixed time for PPS to be active. This is configured with `AT+PPSC=3,<duration>`, and can also be set when enabling PPS with `AT+PPS=1,<duration>`.

##### Command Transmission and AUTOSLEEP

- After the RNWF02 asserts WAKE_RDY, the host DTE can transmit AT commands over UART.

- The RNWF02 remains awake while processing the commands and any corresponding Wi-Fi or protocol activity.

- Once no further commands or traffic are outstanding, the system returns to PPS sleep.

- The AUTOSLEEP parameter controls how long the RNWF02 remains awake after asserting WAKE_RDY, allowing multiple commands to be sent without re-waking each time:

  - Configured with `AT+PPSC=2,<delayms>`, this extends the time RNWF02 stays awake after asserting WAKE_RDY, providing the host extra time to send multiple commands or complete terminal sessions.

---
##### Configuration and Usage

**See example [Configuring and enabling PPS](#EXAMPLE_PPS_1)**

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=21,30</strong></td>
<td>Configure Listen Interval to 30 beacon periods (around 3 seconds)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPSC">+PPSC</a>=1,1</strong></td>
<td>Enable Secondary Oscillator (optional)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPSC">+PPSC</a>=2,100</strong></td>
<td>Set AUTOSLEEP Timeout to 100ms</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPSC">+PPSC</a>=3,60</strong></td>
<td>Set PPS to be enabled for 60 seconds</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPS">+PPS</a>=1</strong></td>
<td>Enable PPS Mode</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPS">+PPS</a>=2,5</strong></td>
<td>Pause PPS temporarily for 5 seconds (timeout extends if sent repeatedly)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPS">+PPS</a>=0</strong></td>
<td>Terminate PPS Operation</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

> [!NOTE]
> - RNWF02 PPS operation requires using the UART wake-up protocol via WAKE_REQ and WAKE_RDY pins. No conventional RTS/CTS hardware flow control is available during PPS.
>
> - To send an AT command, the host DTE must assert WAKE_REQ to wake the device
>
> - When PPS is active, the host DTE cannot send AT commands unless the wake-up protocol is actively used.

---
#### EXtreme Deep Sleep (XDS)

XDS mode puts the RNWF02 into the absolute lowest power state, with all but the bare minimum clocks and peripherals powered off. Use this mode when long idle periods are expected and Wi-Fi connectivity/state retention is not required.

##### XDS characteristics

- The system loses all context and network state (no Wi-Fi connection or open sockets preserved).

- The only wake-up methods available are hardware signals:

  - Pull **MCLR** pin low (hardware reset)

  - Assert the **WAKE_REQ** signal (UART wake protocol)

  - Drive **INT0** pin high

> [!NOTE]
> Wake-up triggers a **full system reboot**.

##### XDS Operation details

To enter XDS mode, send the following command:

`AT+PPS=10`

#### Summary

##### PPS (Platform Power Save)

Balances power saving with connectivity. Maintains Wi-Fi and protocol state. Supports low-latency wake-up via WAKE_REQ/WAKE_RDY pins. Recommended to enable SOSC for precise timing.

##### XDS (EXtreme Deep Sleep)

Maximises power saving by powering down all but the bare minimum device functions. Requires hardware wake-up and full reboot on wake. Used for extended idle periods with no connectivity requirements.

---
### Command Reference:

<a id="AN_CMD_AT_PPS_PPSC"></a>
#### +PPSC

##### Description

This command is used to read or set the PPS configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+PPSC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+PPSC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+PPSC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;SEC_OSC_ENABLED&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>Use secondary oscillator<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Off.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>On.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;AUTO_SLEEP_TIMEOUT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Timeout between commands before entering sleep measured in ms<br />
<br />
Valid range is 10 to 3000<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;DURATION&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Time to maintain PPS mode in seconds (0 for infinite)<br />
<br />
Valid range is 0 to 86400<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_PPS_PPS"></a>
#### +PPS

##### Description

This command allows the firmware to change the state of platform power save.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+PPS=&lt;PPS_STATE&gt;</p></td>
<td style="text-align: left;"><p>PPS<br />
<br />
<a href="#AN_CMD_AT_PPS_PPS_PPS_STATE">PPS_STATE</a> must not be 2</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+PPS=&lt;PPS_STATE&gt;,&lt;PAUSE_TIME&gt;</p></td>
<td style="text-align: left;"><p>PPS<br />
<br />
<a href="#AN_CMD_AT_PPS_PPS_PPS_STATE">PPS_STATE</a> must be 2</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p><span id="AN_CMD_AT_PPS_PPS_PPS_STATE"></span>&lt;PPS_STATE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>PPS State<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disable.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>PPS mode.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>PPS pause sleep.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>XDS mode.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PAUSE_TIME&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>PPS pause time in sec<br />
<br />
Valid range is 1 to 3600<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +PPS

##### Description

**Indication of PPS event.**

| AEC                | Description |
|--------------------|-------------|
| +PPS:\<PPS EVENT\> | PPS Event   |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Event code<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Timeout.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Pause expired.</p></td>
</tr>
</tbody>
</table></td>
</tr>
</tbody>
</table>

---
### Examples:

Configuring and enabling PPS
<a id="EXAMPLE_PPS_1"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_WIFI_WIFIC">+WIFIC</a>=21,30</strong></td>
<td>Configure Listen Interval to 30 beacon periods (around 3 seconds)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPSC">+PPSC</a>=1,1</strong></td>
<td>Enable Secondary Oscillator (optional)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPSC">+PPSC</a>=2,100</strong></td>
<td>Set AUTOSLEEP Timeout to 100ms</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPSC">+PPSC</a>=3,60</strong></td>
<td>Set PPS to be enabled for 60 seconds</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPS">+PPS</a>=1</strong></td>
<td>Enable PPS Mode</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPS">+PPS</a>=2,5</strong></td>
<td>Pause PPS temporarily for 5 seconds (timeout extends if sent repeatedly)</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_PPS_PPS">+PPS</a>=0</strong></td>
<td>Terminate PPS Operation</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

---
## SYSLOG (Module ID = 32)

### Command Reference:

<a id="AN_CMD_AT_SYSLOG_SYSLOGC"></a>
#### +SYSLOGC

##### Description

This command is used to read or set the SYSLOG configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+SYSLOGC</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SYSLOGC=&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+SYSLOGC=&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

<table>
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>&lt;ENABLED&gt;</p></td>
<td style="text-align: left;"><p>Bool<br />
</p></td>
<td style="text-align: left;"><p>DCE’s SYSLOG<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Disabled.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Enabled.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

#### +SYSLOG

##### Description

**SYSLOG Event.**

| AEC | Description |
|----|----|
| +SYSLOG:\<TIMESTAMP\>,\<MODULE_ID\>,\<EVENT_SEVERITY\>,\<MESSAGE\> | Log message |

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
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Log timestamp<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MODULE_ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Module ID<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;EVENT_SEVERITY&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Event severity<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Emergency.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Alert.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Critical.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Error.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>Warning.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>Notice.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>Info.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>Debug.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;MESSAGE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
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

The RNWF02 device has an anti-rollback counter (ARB) which can be used to prevent vulnerable firmware from running on the device.

The value in the ARB is between 0 and 127 and can be increased but never decreased. If a firmware image has a security level which is lower than the value in the ARB, then that image will not boot.

Use the [+ARB](#AN_CMD_AT_ARB_ARB) command to get the current value in the device’s ARB and the current firmware’s security level. If the device’s ARB is lower than the firmware’s security level, then consider increasing the value in the device’s ARB to improve the security of the device.

For information about the security benefits of increasing the device’s ARB, refer to RNWF02 device firmware release notes at microchip.com.

To increase the value in the device’s ARB, use the [+ARB](#AN_CMD_AT_ARB_ARB) command.

> [!CAUTION]
> If the device has an image present in the alternate NVM partition, be aware that increasing the device’s ARB may invalidate that image.

---
### Command Reference:

<a id="AN_CMD_AT_ARB_ARB"></a>
#### +ARB

##### Description

This command is used to get or increase the DCE’s ARB value, and to get the current firmware’s security level.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+ARB</p></td>
<td style="text-align: left;"><p>Get the DCE’s ARB value and the current firmware’s security level<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+ARB=&lt;VALUE&gt;</p></td>
<td style="text-align: left;"><p>Increase the DCE’s ARB value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;VALUE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>The value to which to increase the DCE’s ARB<br />
<br />
Valid range is 1 to 127<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +ARB:\<VALUE\>,\<FW_SECURITY\> | The DCE’s ARB value and the current firmware’s security level |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>DCE’s ARB value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;FW_SECURITY&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Current firmware’s security level<br />
</p></td>
</tr>
</tbody>
</table>

---
---
### Examples:

Example of using [+ARB](#AN_CMD_AT_ARB_ARB)
<a id="EXAMPLE_43ad9746b269d7ef860794a7d75c34ef47c94f97"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_ARB_ARB">+ARB</a></strong></td>
<td>Get the DCE’s ARB value and the current firmware’s security level</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_ARB_ARB">+ARB</a>:0,1</strong></td>
<td>DCE’s ARB value is 0; current firmware’s security level is 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_ARB_ARB">+ARB</a>=1</strong></td>
<td>Increase the DCE’s ARB value to 1</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_ARB_ARB">+ARB</a>:1,1</strong></td>
<td>DCE’s ARB value is 1; current firmware’s security level is 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_ARB_ARB">+ARB</a>=1</strong></td>
<td>Increase the DCE’s ARB value to 1</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_ARB_ARB">+ARB</a>:1,1</strong></td>
<td>DCE’s ARB value is 1; current firmware’s security level is 1</td>
</tr>
<tr>
<td>←</td>
<td><code>ERROR:33.0,"The Value Provided Would Not Increase The ARB"</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_ARB_ARB">+ARB</a>=2</strong></td>
<td>Increase the DCE’s ARB value to 2</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_ARB_ARB">+ARB</a>:1,1</strong></td>
<td>DCE’s ARB value is 1; current firmware’s security level is 1</td>
</tr>
<tr>
<td>←</td>
<td><code>ERROR:33.1,"The Value Provided Would Invalidate The Current Image"</code></td>
<td></td>
</tr>
</tbody>
</table>

---
<a id="AN_MOD_HTTP"></a>
## HTTP (Module ID = 34)

### Introduction

The RNWF02 supports comprehensive HTTP client capabilities via AT commands, enabling easy integration with web servers for a variety of applications such as firmware updates, data retrieval, and cloud communication.

#### Key Features

##### HTTP Configuration Management

Configure HTTP connection parameters including the server address (hostname or IP), port number, request path, TLS settings, timeouts, and more. These settings ensure flexible connection setups to suit diverse network environments and security needs.

##### HTTP GET Requests

Perform HTTP GET operations to request resources from a web server. You can specify the resource path, enabling the retrieval of files, JSON data, or other web content.

##### Direct File Downloads to Flash Filesystem

Download HTTP response data directly into the device’s flash filesystem. By configuring a local filename and file type, the downloaded content is automatically stored in the flash filesystem without requiring manual data reading. This is particularly useful for downloading certificates, configuration files, firmware images, or other persistent data. The filesystem supports multiple file types including USER files, certificates (CERT), private keys (PRIKEY), Diffie-Hellman parameters (DHPARAM), and configuration files (CFG).

##### Data Reading

Efficiently read HTTP response data in chunks of defined length. This allows controlled data transfer suitable for devices with limited memory. Manual data reading can be performed using [+HTTPRD](#AN_CMD_AT_HTTP_HTTPRD) when not downloading directly to the filesystem.

##### Response Handling

Receive detailed response information such as HTTP status codes, response headers, and body content, including full notification when the response body is completely received.

##### Data Integrity Verification

Optional hash calculation (SHA, SHA256, SHA224, SHA512, SHA384) during download to verify data integrity. The hash is computed automatically and reported in the [+HTTPBODYEND](#AN_AEC_AT_HTTP_HTTPBODYEND) asynchronous event.

##### Security Support

Integrated TLS configuration allows HTTPS connections ensuring data privacy and integrity.

#### How It Works

##### Manual Data Retrieval

See examples [HTTPS download](#EXAMPLE_HTTP_1) and [HTTPS download from TCP socket](#EXAMPLE_HTTP_2).

- Configure the HTTP client using [+HTTPC](#AN_CMD_AT_HTTP_HTTPC) to set the hostname, port, path, and other parameters.

- Optionally configure TLS with [+TLSC](#AN_CMD_AT_TLS_TLSC) for encrypted HTTPS connections.

- Initiate an HTTP GET request via [+HTTPGET](#AN_CMD_AT_HTTP_HTTPGET).

- Monitor response status and headers through AECs ([+HTTPRSPCODE](#AN_AEC_AT_HTTP_HTTPRSPCODE), [+HTTPRSPFIELD](#AN_AEC_AT_HTTP_HTTPRSPFIELD)).

- Read the HTTP response body in manageable blocks using [+HTTPRD](#AN_CMD_AT_HTTP_HTTPRD).

- Close the connection cleanly with [+HTTPCL](#AN_CMD_AT_HTTP_HTTPCL) after data transfer completes.

##### Direct Filesystem Download

See example [File download to local filesystem](#EXAMPLE_HTTP_3).

- Configure the HTTP client using [+HTTPC](#AN_CMD_AT_HTTP_HTTPC) to set the hostname, port, path, and other parameters.

- Set the local filename using [+HTTPC](#AN_CMD_AT_HTTP_HTTPC) ID 20 (FILENAME parameter).

- Set the local file type using [+HTTPC](#AN_CMD_AT_HTTP_HTTPC) ID 21 (FILETYPE parameter):

  - 0 = USER (user files)

  - 1 = CERT (certificates)

  - 2 = PRIKEY (private keys)

  - 3 = DHPARAM (Diffie-Hellman parameters)

  - 20 = CFG (configuration files)

- Optionally configure hash verification using [+HTTPC](#AN_CMD_AT_HTTP_HTTPC) ID 22 (CHECK_MODE parameter):

  - 0 = NONE (no hash verification)

  - 10 = SHA

  - 11 = SHA256

  - 12 = SHA224

  - 13 = SHA512

  - 14 = SHA384

- Optionally configure TLS with [+TLSC](#AN_CMD_AT_TLS_TLSC) for encrypted HTTPS connections.

- Initiate an HTTP GET request via [+HTTPGET](#AN_CMD_AT_HTTP_HTTPGET).

- Monitor response status and headers through AECs ([+HTTPRSPCODE](#AN_AEC_AT_HTTP_HTTPRSPCODE), [+HTTPRSPFIELD](#AN_AEC_AT_HTTP_HTTPRSPFIELD)).

- The downloaded data is automatically written to the flash filesystem.

- When complete, [+HTTPBODYEND](#AN_AEC_AT_HTTP_HTTPBODYEND) is sent with total bytes downloaded and optional hash value.

- A filesystem update notification [+FSUP](#AN_AEC_AT_FS_FLFS_FSUP) confirms the file has been stored.

- The connection closes automatically (non-persistent connection mode).

> [!NOTE]
> When a local filename is configured, the HTTP client operates in non-persistent connection mode and automatically writes received data to the filesystem. Manual data reading via [+HTTPRD](#AN_CMD_AT_HTTP_HTTPRD) is not available in this mode.

#### Advanced Features

##### Using an Existing Socket Connection

The HTTP client can utilize an existing TCP socket connection instead of creating its own. This is useful when you need more control over the connection setup, such as pre-configuring socket options or managing connection pooling.

> [!NOTE]
> When using an existing socket, do not configure the HOST (ID 2) or PORT (ID 3) parameters in the HTTP configuration.

##### Path Override with Query Parameters

When issuing an HTTP GET request, you can specify a complete path including query parameters and fragments as the second parameter to [+HTTPGET](#AN_CMD_AT_HTTP_HTTPGET). This overrides the PATH (ID 4) and FILE (ID 5) configuration parameters for that specific request.

See example [HTTPGET with path and query/fragments](#EXAMPLE_HTTP_4).

##### HTTP Authentication

HTTP basic authentication can be implemented by providing additional request headers using [+HTTPC](#AN_CMD_AT_HTTP_HTTPC) ID 8 (REQ_HEADERS parameter). The authorization header should contain the Base64-encoded credentials.

See example [HTTP basic authentication using additional request headers](#EXAMPLE_HTTP_5).

##### Reading Configuration Values

The read-only configuration parameter **CONTENT_LENGTH** reports the Content-Length value from the HTTP response headers after they are received.

---
### Command Reference:

<a id="AN_CMD_AT_HTTP_HTTPC"></a>
#### +HTTPC

##### Description

This command is used to read or set the HTTP configuration.

This command is a configuration command which supports setting and getting parameter values. The behaviour of configuration commands is described in general in the [Configuration Commands](#_configuration_commands) section.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+HTTPC</p></td>
<td style="text-align: left;"><p>Query configuration list<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+HTTPC=&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Query all configuration elements<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+HTTPC=&lt;CONF&gt;,&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Query a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+HTTPC=&lt;CONF&gt;,&lt;ID&gt;,&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Set a single element<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Parameter ID number<br />
<br />
Unsigned 8-bit value<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;VAL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
String<br />
Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Parameter value<br />
</p></td>
</tr>
</tbody>
</table>

| Response                 | Description   |
|--------------------------|---------------|
| +HTTPC:\<CONF\>,\<CONF\> | List response |
| +HTTPC:\<ID\>,\<VAL\>    | Read response |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ID&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
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
<caption>Configuration Parameters</caption>
<colgroup>
<col style="width: 4%" />
<col style="width: 28%" />
<col style="width: 14%" />
<col style="width: 46%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">ID</th>
<th style="text-align: left;">Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>&lt;PRESET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration preset<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>Default.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>&lt;HOST&gt;</p></td>
<td style="text-align: left;"><p>String<br />
IPv4 Address<br />
IPv6 Address<br />
</p></td>
<td style="text-align: left;"><p>Host domain name or IP address<br />
Maximum length of string is 255<br />
Format of IPv4 address is 'a.b.c.d'<br />
Format of IPv6 address is 'a:b:c:d::e:f'<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>&lt;PORT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Listening port<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>4</p></td>
<td style="text-align: left;"><p>&lt;PATH&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Path to remote file<br />
Maximum length of string is 1024<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>5</p></td>
<td style="text-align: left;"><p>&lt;FILE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Remote filename<br />
Maximum length of string is 1024<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>6</p></td>
<td style="text-align: left;"><p>&lt;TIMEOUT&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Timeout in seconds<br />
<br />
Positive unsigned 8-bit value<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>7</p></td>
<td style="text-align: left;"><p>&lt;TLS_CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>TLS configuration index (see +TLSC)<br />
<br />
Valid range is 0 to 4<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>8</p></td>
<td style="text-align: left;"><p>&lt;REQ_HEADERS&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Additional request headers<br />
Maximum length of string is 1024<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>&lt;SOCKET_ID&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Socket ID<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>&lt;FILENAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Local filename<br />
Maximum length of string is 32<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>21</p></td>
<td style="text-align: left;"><p>&lt;FILETYPE&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Local file type<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>User.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>1</p></td>
<td style="text-align: left;"><p>Certificate.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>2</p></td>
<td style="text-align: left;"><p>Private Key.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>3</p></td>
<td style="text-align: left;"><p>Diffie-Hellman parameters.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>20</p></td>
<td style="text-align: left;"><p>Configuration File.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>22</p></td>
<td style="text-align: left;"><p>&lt;CHECK_MODE&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Checking mode<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>0</p></td>
<td style="text-align: left;"><p>None.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>40</p></td>
<td style="text-align: left;"><p>&lt;CONTENT_LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
(Read Only)</p></td>
<td style="text-align: left;"><p>Content length<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>100</p></td>
<td style="text-align: left;"><p>&lt;ASYNC_NEXT_OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Async next data offset<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>101</p></td>
<td style="text-align: left;"><p>&lt;ASYNC_WIN_SZ&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Async window size<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>102</p></td>
<td style="text-align: left;"><p>&lt;ASYNC_MAX_FRM_SZ&gt;</p></td>
<td style="text-align: left;"><p>Unsigned Integer<br />
</p></td>
<td style="text-align: left;"><p>Async maximum frame size<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_HTTP_HTTPGET"></a>
#### +HTTPGET

##### Description

This command performs an HTTP GET operation.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+HTTPGET=&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Perform an HTTP GET operation<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
<tr>
<td style="text-align: left;"><p>AT+HTTPGET=&lt;CONF&gt;,&lt;PATH&gt;</p></td>
<td style="text-align: left;"><p>Perform an HTTP GET operation for a path<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PATH&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>Resource path<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_HTTP_HTTPRD"></a>
#### +HTTPRD

##### Description

This command performs an HTTP data read operation.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+HTTPRD=&lt;CONF&gt;,&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Read HTTP data<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;LENGTH&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of bytes<br />
</p></td>
</tr>
</tbody>
</table>

| Response | Description |
|----|----|
| +HTTPRD:\<CONF\>,\<DATA_LEN\>,\<DATA_OFFSET\>,\<DATA\> | HTTP body data read |

**Response Syntax**

<table>
<caption>Response Element Syntax</caption>
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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LEN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Offset of data bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>HTTP data<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_CMD_AT_HTTP_HTTPCL"></a>
#### +HTTPCL

##### Description

This command performs an HTTP close operation.

**Security**

Default [security](#_security_model) for the command is: `GGGG`

<table>
<caption>Command Syntax</caption>
<colgroup>
<col style="width: 66%" />
<col style="width: 28%" />
<col style="width: 5%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Command</th>
<th style="text-align: left;">Description</th>
<th style="text-align: left;"><a href="#_security_model">Sec</a></th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>AT+HTTPCL=&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Close HTTP session<br />
</p></td>
<td style="text-align: left;"><p><code>GGGG</code></p></td>
</tr>
</tbody>
</table>

<table>
<caption>Command Parameter Syntax</caption>
<colgroup>
<col style="width: 21%" />
<col style="width: 15%" />
<col style="width: 62%" />
</colgroup>
<thead>
<tr>
<th style="text-align: left;">Parameter Name</th>
<th style="text-align: left;">Type</th>
<th style="text-align: left;">Description</th>
</tr>
</thead>
<tbody>
<tr>
<td style="text-align: left;"><p>&lt;CONF&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
</tbody>
</table>

---
### AEC Reference:

<a id="AN_AEC_AT_HTTP_HTTPRSPCODE"></a>
#### +HTTPRSPCODE

##### Description

**HTTP response code.**

| AEC                                                 | Description        |
|-----------------------------------------------------|--------------------|
| +HTTPRSPCODE:\<CONF\>,\<RSP_PROTOCOL\>,\<RSP_CODE\> | HTTP response code |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_PROTOCOL&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP response protocol version<br />
<br />
Value is 1.1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_CODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
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
#### +HTTPRSPFIELD

##### Description

**HTTP response field.**

| AEC | Description |
|----|----|
| +HTTPRSPFIELD:\<CONF\>,\<RSP_FIELD_NAME\>,\<RSP_FIELD_VALUE\> | HTTP response field |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_FIELD_NAME&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>HTTP response field name<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;RSP_FIELD_VALUE&gt;</p></td>
<td style="text-align: left;"><p>String<br />
</p></td>
<td style="text-align: left;"><p>HTTP response field value<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_HTTP_HTTPBODYRX"></a>
#### +HTTPBODYRX

##### Description

**HTTP body.**

| AEC | Description |
|----|----|
| +HTTPBODYRX:\<CONF\>,\<PEND_DATA\> | HTTP body data notify |
| +HTTPBODYRX:\<CONF\>,\<DATA_LEN\>,\<DATA_OFFSET\>,\<DATA\> | HTTP body data received |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;PEND_DATA&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Number of pending bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LEN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_OFFSET&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Offset of data bytes<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>HTTP data<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_HTTP_HTTPBODYEND"></a>
#### +HTTPBODYEND

##### Description

**HTTP body end.**

| AEC | Description |
|----|----|
| +HTTPBODYEND:\<CONF\>,\<DATA_LEN\> | HTTP body data end |
| +HTTPBODYEND:\<CONF\>,\<DATA_LEN\>,\<HASH_TYPE\>,\<HASH\> | HTTP body data end |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;DATA_LEN&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Length of data<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;HASH_TYPE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Hash algorithm<br />
</p>
<table>
<colgroup>
<col style="width: 14%" />
<col style="width: 85%" />
</colgroup>
<tbody>
<tr>
<td style="text-align: left;"><p>10</p></td>
<td style="text-align: left;"><p>SHA.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>11</p></td>
<td style="text-align: left;"><p>SHA256.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>12</p></td>
<td style="text-align: left;"><p>SHA224.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>13</p></td>
<td style="text-align: left;"><p>SHA512.</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>14</p></td>
<td style="text-align: left;"><p>SHA384.</p></td>
</tr>
</tbody>
</table></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;HASH&gt;</p></td>
<td style="text-align: left;"><p>Byte Array<br />
</p></td>
<td style="text-align: left;"><p>Hash<br />
</p></td>
</tr>
</tbody>
</table>

---
<a id="AN_AEC_AT_HTTP_HTTPCL"></a>
#### +HTTPCL

##### Description

**HTTP close.**

| AEC              | Description |
|------------------|-------------|
| +HTTPCL:\<CONF\> | HTTP close  |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
</tbody>
</table>

---
#### +HTTPERR

##### Description

**HTTP error.**

| AEC                              | Description |
|----------------------------------|-------------|
| +HTTPERR:\<CONF\>,\<ERROR_CODE\> | HTTP error  |

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
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>HTTP Configuration number<br />
<br />
Value is 1<br />
</p></td>
</tr>
<tr>
<td style="text-align: left;"><p>&lt;ERROR_CODE&gt;</p></td>
<td style="text-align: left;"><p>Integer<br />
</p></td>
<td style="text-align: left;"><p>Error code<br />
</p>
<p>See <a href="#_status_response_codes">Status Response Codes</a></p></td>
</tr>
</tbody>
</table>

---
### Examples:

HTTPS download
<a id="EXAMPLE_HTTP_1"></a>

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_TIME_TIME">+TIME</a>:3969426905</strong></td>
<td>Wait for time for correct TLS operation</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,1,"ServerCACert"</strong></td>
<td>Set the server CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,6,"example.com"</strong></td>
<td>Set the server domain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,2,"www.example.com"</strong></td>
<td>Set the server hostname</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,3,443</strong></td>
<td>Set the HTTPS port number</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,5,"/examplefile.bin"</strong></td>
<td>Set the file path</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,6,10</strong></td>
<td>Set 10 second timeout</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,7,1</strong></td>
<td>Use TLSC index 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPGET">+HTTPGET</a>=1</strong></td>
<td>Get resource configuration 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPCODE">+HTTPRSPCODE</a>:1,1.1,200</strong></td>
<td>Server responds 200 OK</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Date","Wed, 5 Nov 2025 11:23:45 GMT"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Last-Modified","Sun, 12 Oct 2025 21:15:27 GMT"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Accept-Ranges","bytes"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Content-Type","binary/octet-stream"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Content-Length","2563"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPBODYRX">+HTTPBODYRX</a>:1,1460</strong></td>
<td>1460 bytes received</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>=1,1460</strong></td>
<td>Read 1460 bytes</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>:1,1460,0,\[FFFFFFFF…​74780000\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPBODYRX">+HTTPBODYRX</a>:1,1103</strong></td>
<td>1103 bytes received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPBODYEND">+HTTPBODYEND</a>:1,2563</strong></td>
<td>All body data received</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>=1,1103</strong></td>
<td>Read 1103 bytes</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>:1,1103,1460,\[65205072…​1102D0A1\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPCL">+HTTPCL</a>:1</strong></td>
<td>Remote server closed connection</td>
</tr>
</tbody>
</table>

HTTPS download from TCP socket
<a id="EXAMPLE_HTTP_2"></a>

<table>
<tbody>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_TIME_TIME">+TIME</a>:3969426905</strong></td>
<td>Wait for time for correct TLS operation</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>=2</strong></td>
<td>Open TCP socket</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_SOCKET_SOCKO">+SOCKO</a>:18870</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,1,"ServerCACert"</strong></td>
<td>Set the server CA certificate</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_TLS_TLSC">+TLSC</a>=1,6,"example.com"</strong></td>
<td>Set the server domain</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,5,"/examplefile.bin"</strong></td>
<td>Set the file path</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,6,10</strong></td>
<td>Set 10 second timeout</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,10,18870</strong></td>
<td>Assign socket ID to HTTP configuration</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKTLS">+SOCKTLS</a>=18870,1</strong></td>
<td>Upgrade socket to TLS</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_SOCKET_SOCKBR">+SOCKBR</a>=18870,"www.example.com",443</strong></td>
<td>Bind socket to server</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKIND">+SOCKIND</a>:18870,"1.2.3.4",61955,"5.6.7.8",443</strong></td>
<td>Socket connected</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_SOCKET_SOCKTLS">+SOCKTLS</a>:18870</strong></td>
<td>Socket upgraded to TLS</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPGET">+HTTPGET</a>=1</strong></td>
<td>Get resource configuration 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPCODE">+HTTPRSPCODE</a>:1,1.1,200</strong></td>
<td>Server responds 200 OK</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Date","Wed, 5 Nov 2025 11:23:45 GMT"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Last-Modified","Sun, 12 Oct 2025 21:15:27 GMT"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Accept-Ranges","bytes"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Content-Type","binary/octet-stream"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Content-Length","2563"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPBODYRX">+HTTPBODYRX</a>:1,1460</strong></td>
<td>1460 bytes received</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>=1,1460</strong></td>
<td>Read 1460 bytes</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>:1,1460,0,\[FFFFFFFF…​74780000\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPBODYRX">+HTTPBODYRX</a>:1,1103</strong></td>
<td>1103 bytes received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPBODYEND">+HTTPBODYEND</a>:1,2563</strong></td>
<td>All body data received</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>=1,1103</strong></td>
<td>Read 1103 bytes</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_HTTP_HTTPRD">+HTTPRD</a>:1,1103,1460,\[65205072…​1102D0A1\]</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPCL">+HTTPCL</a>:1</strong></td>
<td>Remote server closed connection</td>
</tr>
</tbody>
</table>

File download to local filesystem
<a id="EXAMPLE_HTTP_3"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,20,"testname"</strong></td>
<td>Set local filename</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,21,0</strong></td>
<td>Set local file type to USER</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPGET">+HTTPGET</a>=1</strong></td>
<td>Get resource configuration 1</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPCODE">+HTTPRSPCODE</a>:1,1.1,200</strong></td>
<td>Server responds 200 OK</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Date","Wed, 5 Nov 2025 11:23:45 GMT"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Last-Modified","Sun, 12 Oct 2025 21:15:27 GMT"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Accept-Ranges","bytes"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Content-Type","binary/octet-stream"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPFIELD">+HTTPRSPFIELD</a>:1,"Content-Length","1024"</strong></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPBODYEND">+HTTPBODYEND</a>:1,1024</strong></td>
<td>All body data received</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_FS_FLFS_FSUP">+FSUP</a>:1,0,"testname",1024</strong></td>
<td>Filesystem updated</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPCL">+HTTPCL</a>:1</strong></td>
<td>Remote server closed connection</td>
</tr>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>=2,0</strong></td>
<td>Query for USER files</td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_CMD_AT_FS_FLFS_FS">+FS</a>:2,0,"testname"</strong></td>
<td>File now present in filesystem</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
</tbody>
</table>

HTTPGET with path and query/fragments
<a id="EXAMPLE_HTTP_4"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPGET">+HTTPGET</a>=1,"/anypath/anyfile?att1=val1&att2=val2</strong></td>
<td>afragment"</td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
<td></td>
</tr>
<tr>
<td>←</td>
<td><strong><a href="#AN_AEC_AT_HTTP_HTTPRSPCODE">+HTTPRSPCODE</a>:1,1.1,200</strong></td>
<td></td>
</tr>
</tbody>
</table>

HTTP basic authentication using additional request headers
<a id="EXAMPLE_HTTP_5"></a>

<table>
<tbody>
<tr>
<td>→</td>
<td><strong>AT<a href="#AN_CMD_AT_HTTP_HTTPC">+HTTPC</a>=1,8,"Authorization: Basic dXNlcm5hbWU6cGFzc3dk"</strong></td>
</tr>
<tr>
<td>←</td>
<td><code>OK</code></td>
</tr>
</tbody>
</table>

---
## List of Examples

<table>
<tbody>
<tr>
<td>Module</td>
<td>Description</td>
</tr>
<tr>
<td>Configuration Commands</td>
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
<td>FS</td>
<td><a href="#EXAMPLE_c3a29205005bd88d52fee5b4c1257e7f8c4851de">File transfer using XModem+CRC with +FS</a></td>
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
<td><a href="#EXAMPLE_TLS_DIGEST">Peer certificate digest pinning with +TLSC</a></td>
</tr>
<tr>
<td>WSCN</td>
<td><a href="#EXAMPLE_WSCN_SECURITY">Scan for Access Points and filter by security type</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_286d6c7f74c01a7bacc3d6fcaa240ad067b1f736">Setting SSID filter with +WSCNC</a></td>
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
<td><a href="#EXAMPLE_b24cb7601966bd304010fa7449e5f57c0507b958">Query device information with +DI</a></td>
</tr>
<tr>
<td>EXTCRYPTO</td>
<td><a href="#EXAMPLE_EXTCRYPTO_TLS">Example of TLS configuration for secure signing via external crypto operations</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_EXTCRYPTO">Example of signing request/response using +EXTCRYPTO</a></td>
</tr>
<tr>
<td>WIFI</td>
<td><a href="#EXAMPLE_83aadd2a5891271329d9dc62f4cea81d34571a9e">Settings with +WIFIC</a></td>
</tr>
<tr>
<td></td>
<td><a href="#EXAMPLE_c37bae967b299185b054858a003c7507e0b388a9">+WIFIC coexistence settings for 3-wire PTA interface</a></td>
</tr>
<tr>
<td>NVM</td>
<td><a href="#EXAMPLE_NVM_EXAMPLE">Simple example of NVM usage</a></td>
</tr>
<tr>
<td>DFU</td>
<td><a href="#EXAMPLE_154f5dd58fe255da7480e1634642e778c98de910">Example of using +DFUADR and +DFUSEQ</a></td>
</tr>
<tr>
<td>PPS</td>
<td><a href="#EXAMPLE_PPS_1">Configuring and enabling PPS</a></td>
</tr>
<tr>
<td>ARB</td>
<td><a href="#EXAMPLE_43ad9746b269d7ef860794a7d75c34ef47c94f97">Example of using +ARB</a></td>
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