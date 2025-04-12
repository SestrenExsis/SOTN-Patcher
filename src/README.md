# Other notes

Entity Room Index is comprised of:
- entity room index
- entity slot

# Notes for Clock Hand mod

### Clock Hands in Marble Gallery and Black Marble Gallery
```
$2CC(a1) = game time, hours unit
$2D0(a1) = game time, minutes unit
$2D4(a1) = game time, seconds unit
Old logic:
... 360 units of minute hand = 60 * MINUTES
... 3600 units of hour hand = 300 * HOURS + 5 * MINUTES
New logic:
... 3600 units of minute hand = 60 * SECONDS
... 3600 units of hour hand = 60 * MINUTES
-------------------------
@ 0x801CCC2C (+0x00) : 0x8CA302D0 = lw v1,$2D0(a1) -> lw v1,$2D4(a1) = 0x8CA302D4
...
@ 0x801CCC44 (+0x18) : 0x8CA302CC = lw v1,$2CC(a1) -> nop            = 0x00000000
...
@ 0x801CCC4C (+0x20) : 0x00031080 = sll v0,v1,$2   -> nop            = 0x00000000
@ 0x801CCC50 (+0x24) : 0x00431021 = addu v0,v1     -> nop            = 0x00000000
@ 0x801CCC54 (+0x28) : 0x00021900 = sll v1,v0,$4   -> sll v1,a1,$4   = 0x00051900
@ 0x801CCC58 (+0x2C) : 0x00621823 = subu v1,v0     -> subu v1,a1     = 0x00651823
...
@ 0x801CCC60 (+0x34) : 0x00051080 = sll v0,a1,$2   -> nop            = 0x00000000
@ 0x801CCC64 (+0x38) : 0x00451021 = addu v0,a1     -> nop            = 0x00000000
@ 0x801CCC68 (+0x3C) : 0x00621821 = addu v1,v0     -> nop            = 0x00000000
```

### Clock Hands in Maria Clock Room Cutscene
```
$2CC(s3) = game time, hours unit
$2D0(s3) = game time, minutes unit
$2D4(s3) = game time, seconds unit
-------------------------
@ 0x80198494 (+0x00) : 0x8E6302D0 = lw v1,$2D0(s3) -> lw v1,$2D4(s3) = 0x8E6302D4
...
@ 0x801984AC (+0x18) : 0x8E6302CC = lw v1,$2CC(s3) -> nop            = 0x00000000
... 
@ 0x801984B4 (+0x20) : 0x00031080 = sll v0,v1,$2   -> nop            = 0x00000000
@ 0x801984B8 (+0x24) : 0x00431021 = addu v0,v1     -> nop            = 0x00000000
@ 0x801984BC (+0x28) : 0x00021900 = sll v1,v0,$4   -> sll v1,a0,$4   = 0x00041900
@ 0x801984C0 (+0x2C) : 0x00621823 = subu v1,v0     -> subu v1,a0     = 0x00641823
...
@ 0x801984C8 (+0x34) : 0x00041080 = sll v0,a0,$2   -> nop            = 0x00000000
@ 0x801984CC (+0x38) : 0x00441021 = addu v0,a0     -> nop            = 0x00000000
@ 0x801984D0 (+0x3C) : 0x00621821 = addu v1,v0     -> nop            = 0x00000000
```
