# Common ARM Cortex-M Peripherals

This reference provides information about commonly found peripherals in ARM Cortex-M microcontrollers.

## Standard ARM Peripherals

### System Control Block (SCB)
Base address typically at 0xE000ED00. Controls core configuration and provides status information.

Common registers:
- **CPUID**: CPU identification
- **ICSR**: Interrupt control and state
- **VTOR**: Vector table offset
- **AIRCR**: Application interrupt and reset control
- **SCR**: System control register
- **SHCSR**: System handler control and state

### NVIC (Nested Vectored Interrupt Controller)
Base address typically at 0xE000E100. Manages interrupts and exceptions.

Common register groups:
- **ISER[]**: Interrupt set-enable registers
- **ICER[]**: Interrupt clear-enable registers
- **ISPR[]**: Interrupt set-pending registers
- **ICPR[]**: Interrupt clear-pending registers
- **IPR[]**: Interrupt priority registers

### SysTick Timer
Base address typically at 0xE000E010. 24-bit countdown timer.

Registers:
- **CTRL**: Control and status
- **LOAD**: Reload value
- **VAL**: Current value
- **CALIB**: Calibration value

## Vendor-Specific Peripherals

### GPIO (General Purpose I/O)
Configuration varies by vendor. Common register patterns:

- **MODE/MODER**: Pin mode configuration (input/output/alternate/analog)
- **OTYPE/OTYPER**: Output type (push-pull/open-drain)
- **OSPEED/OSPEEDR**: Output speed
- **PUPD/PUPDR**: Pull-up/pull-down configuration
- **IDR**: Input data register (read)
- **ODR**: Output data register (read/write)
- **BSRR**: Bit set/reset register (atomic operations)

### Timers
Basic timer registers:
- **CR1/CR2**: Control registers
- **DIER**: DMA/interrupt enable
- **SR**: Status register
- **CNT**: Counter value
- **PSC**: Prescaler
- **ARR**: Auto-reload register
- **CCR[]**: Capture/compare registers

### UART/USART
Common registers:
- **CR1/CR2/CR3**: Control registers
- **BRR**: Baud rate register
- **SR/ISR**: Status register
- **DR/RDR/TDR**: Data registers

### SPI
Common registers:
- **CR1/CR2**: Control registers
- **SR**: Status register
- **DR**: Data register

### I2C
Common registers:
- **CR1/CR2**: Control registers
- **OAR1/OAR2**: Own address registers
- **DR**: Data register
- **SR1/SR2**: Status registers
- **CCR**: Clock control register

## Common Register Access Types

- **read-only**: Register can only be read
- **write-only**: Register can only be written
- **read-write**: Register can be both read and written
- **read-writeOnce**: Can be written only once after reset

## Common Bit Field Patterns

### Enable/Disable Bits
Usually bit 0, commonly named EN, ENABLE, or similar.

### Status Flags
Often in status registers (SR), indicate peripheral state:
- **TXE**: Transmit buffer empty
- **RXNE**: Receive buffer not empty
- **BUSY**: Peripheral busy
- **OVR**: Overrun error

### Interrupt Enable Bits
Mirror status flags but control interrupt generation:
- **TXEIE**: TX empty interrupt enable
- **RXNEIE**: RX not empty interrupt enable
