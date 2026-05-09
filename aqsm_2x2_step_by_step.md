# AQSM/HDWM Worked Example: 2x2 Watermark Into 4x4 Carrier

This note walks through one complete, code-ready example of the paper's model:

- watermark image size: `2x2`
- carrier image size: `4x4`
- scale factor: `r = 1`
- grayscale depth: 8 bits

I use `r = 1` because the paper explicitly states the three AQSM watermark images that are actually embedded for this case. The paper does not fully specify the general AQSM customization schedule for every larger `r`, so this walkthrough avoids inventing that missing behavior.

## Sources Reviewed

- Local paper: `adaptive quantum scaling model.pdf`
- Local TeX source: `arxiv_src/A3_Manuscript.tex`
- Existing explanation: `paper_analysis.md`
- Online check: arXiv `2502.18006`, current listed version `v2`, last revised `2025-03-31`: https://arxiv.org/abs/2502.18006

## What Is Confirmed And What Is Assumed

Confirmed from the paper/source:

- AQSM has preparation, customization, and aggregation stages.
- Preparation decomposes the 8-bit watermark into 8 bit planes.
- For `r = 1`, the paper embeds three AQSM outputs built from these four-block sets:
  - `{w1, w2, w3, w4}`
  - `{w5, w7, w7, w7}`
  - `{w6, w8, w8, w8}`
- QBA combines four equally sized binary blocks into a larger binary block by placing them at top-left, top-right, bottom-left, and bottom-right.
- HDWM uses watermark histogram parameters `tau1`, `tau2`, and a carrier-MSB xor value `V_eta`.
- For `r = 1`, `eta = 0`, so `V_eta` is based on the xor of 3 carrier MSBs.
- Extraction reverses embedding, applies inverse QBA, then uses majority voting for repeated bit planes.

Implementation conventions used here:

- A pixel bit string is written as `b7 b6 b5 b4 b3 b2 b1 b0`, where `b7` is the MSB and `b0` is the LSB.
- `w1 = b0`, `w2 = b1`, ..., `w8 = b7`.
- The first, second, and third LSB carrier planes are `b0`, `b1`, and `b2`.
- For `V_eta` when `eta = 0`, use `V = b7 xor b6 xor b5`.

Paper ambiguity avoided in the example:

- The paper defines `T_dark` with denominator `2^m x 2^n`, but a watermark of size `2^m x 2^m` naturally has `2^(2m)` pixels. This note does not silently correct the paper. Instead, it uses an all-bright `2x2` watermark, so both denominators give the same HDWM branch: `tau1 = 1`, `tau2 = 1`.

## Code-Ready Definitions

For a binary bit `a`, `1 - a` means logical NOT.

For one carrier pixel and one watermark bit:

- `w`: AQSM watermark bit to embed
- `b`: carrier LSB-plane bit before embedding
- `b_prime`: carrier LSB-plane bit after embedding
- `V`: xor of selected carrier MSBs

The HDWM embedding table is equivalent to:

```text
if tau1 == 0:
    b_prime = w
elif tau1 == 1 and tau2 == 0:
    b_prime = w xor V
elif tau1 == 1 and tau2 == 1:
    b_prime = w xor (1 - V)
```

The extraction table is the inverse:

```text
if tau1 == 0:
    w_hat = b_prime
elif tau1 == 1 and tau2 == 0:
    w_hat = b_prime xor V
elif tau1 == 1 and tau2 == 1:
    w_hat = b_prime xor (1 - V)
```

For setting carrier bit plane `p` to a target bit `b_prime`:

```text
new_pixel = (old_pixel & ~(1 << p)) | (b_prime << p)
```

where `p = 0` for the first LSB, `p = 1` for the second LSB, and `p = 2` for the third LSB.

## Step 1: Choose The Input Images

Use this `2x2` watermark `W`:

```text
W =
[[130, 200],
 [170, 255]]
```

Binary form:

```text
130 = 10000010
200 = 11001000
170 = 10101010
255 = 11111111
```

Use this `4x4` carrier `C`:

```text
C =
[[212,  47, 133,  88],
 [ 17, 190,  64, 251],
 [102,  73, 155,  36],
 [240, 121,  12, 201]]
```

Binary form:

```text
[[11010100, 00101111, 10000101, 01011000],
 [00010001, 10111110, 01000000, 11111011],
 [01100110, 01001001, 10011011, 00100100],
 [11110000, 01111001, 00001100, 11001001]]
```

## Step 1A: Formal NEQR Encoding

The paper first represents grayscale images with NEQR before applying AQSM and HDWM. In a code simulation, we can usually keep the image as a matrix of 8-bit integers, but NEQR explains what the paper means by "quantum image."

For a `2^s x 2^s` grayscale image with 8-bit pixels, NEQR stores each pixel as:

```text
|grayscale bits>|Y coordinate bits>|X coordinate bits>
```

The general form is:

```text
|I> = (1 / 2^s) * sum over all Y,X of |C(Y,X)>|YX>
```

where:

```text
C(Y,X) = 8-bit grayscale value at row Y, column X
Y      = row coordinate
X      = column coordinate
```

The factor `1 / 2^s` normalizes the quantum state because there are:

```text
2^s * 2^s = 2^(2s)
```

coordinate positions, and each has amplitude `1 / 2^s`.

### NEQR Encoding Of The 2x2 Watermark

The watermark has size:

```text
2x2 = 2^1 x 2^1
```

so:

```text
s = m = 1
```

It needs:

```text
8 grayscale qubits
1 Y-coordinate qubit
1 X-coordinate qubit
total = 10 qubits
```

Using row-major coordinates:

```text
W[0,0] = 130 = 10000010, coordinate |00>
W[0,1] = 200 = 11001000, coordinate |01>
W[1,0] = 170 = 10101010, coordinate |10>
W[1,1] = 255 = 11111111, coordinate |11>
```

Therefore:

```text
|W> = 1/2 * (
    |10000010>|00>
  + |11001000>|01>
  + |10101010>|10>
  + |11111111>|11>
)
```

This is the formal quantum representation of the same matrix:

```text
[[130, 200],
 [170, 255]]
```

### NEQR Encoding Of The 4x4 Carrier

The carrier has size:

```text
4x4 = 2^2 x 2^2
```

so:

```text
s = n = 2
```

It needs:

```text
8 grayscale qubits
2 Y-coordinate qubits
2 X-coordinate qubits
total = 12 qubits
```

The normalization factor is:

```text
1 / 2^n = 1 / 4
```

The coordinate basis uses two bits for `Y` and two bits for `X`:

```text
row 0 -> Y = 00
row 1 -> Y = 01
row 2 -> Y = 10
row 3 -> Y = 11

col 0 -> X = 00
col 1 -> X = 01
col 2 -> X = 10
col 3 -> X = 11
```

So the full carrier state is:

```text
|C> = 1/4 * (
    |11010100>|0000> + |00101111>|0001> + |10000101>|0010> + |01011000>|0011>
  + |00010001>|0100> + |10111110>|0101> + |01000000>|0110> + |11111011>|0111>
  + |01100110>|1000> + |01001001>|1001> + |10011011>|1010> + |00100100>|1011>
  + |11110000>|1100> + |01111001>|1101> + |00001100>|1110> + |11001001>|1111>
)
```

In each coordinate ket `|YX>`, the first two bits are `Y` and the last two bits are `X`.

For example:

```text
C[2,3] = 36 = 00100100
Y = 2 = 10
X = 3 = 11
|YX> = |1011>

So this term is:
|00100100>|1011>
```

### Do We Need To Build The NEQR State In Code?

For this walkthrough, no.

The rest of the example uses classical matrices because the paper's own experiments are MATLAB simulations, and the AQSM/HDWM logic can be implemented exactly with arrays and bit operations.

The implementation mapping is:

```text
NEQR grayscale qubits    <->  8-bit integer pixel values
NEQR coordinate qubits   <->  matrix row/column indices
bit-plane decomposition  <->  (pixel >> bit_index) & 1
QBA block splicing       <->  array quadrant concatenation
HDWM bit embedding       <->  set selected LSB plane bits
```

So NEQR should be understood first conceptually, but an implementation can start from the `uint8` image matrix unless the goal is to build actual quantum circuits.

## Step 2: Compute Scale Parameters

This step decides how much the watermark must be expanded so that it can be embedded into the carrier.

The paper uses several parameters:

```text
m     describes the watermark size
n     describes the carrier size
r     describes the size gap between carrier and watermark
beta  helper parameter used by AQSM to compute alpha
alpha controls how many low/high bit-plane block sets AQSM prepares
d     QBA aggregation depth, meaning how many times 4 blocks are merged into 1 larger block
q     number of AQSM binary watermark images output after QBA
```

### Meaning Of m

The watermark is `2^m x 2^m = 2x2`, so:

```text
m = 1
```

because:

```text
2^1 = 2
```

So `m` is not the number of pixels. It is the exponent that describes one side length of the square watermark image.

The total number of watermark pixels is:

```text
2^m * 2^m = 2^(2m) = 2^2 = 4
```

### Meaning Of n

The carrier is `2^n x 2^n = 4x4`, so:

```text
n = 2
```

because:

```text
2^2 = 4
```

So `n` is the exponent that describes one side length of the square carrier image.

The total number of carrier pixels is:

```text
2^n * 2^n = 2^(2n) = 2^4 = 16
```

### Meaning Of r

The scale factor is:

```text
r = n - m = 2 - 1 = 1
```

`r` tells us how many powers of two larger the carrier side length is than the watermark side length.

Here:

```text
carrier side length / watermark side length = 4 / 2 = 2
```

and:

```text
2^r = 2^1 = 2
```

So the carrier is `2` times wider and `2` times taller than the watermark.

In area:

```text
carrier pixels / watermark pixels = 16 / 4 = 4
```

and:

```text
4^r = 4^1 = 4
```

So AQSM must spread each kind of watermark bit-plane information across a `4x` larger pixel grid.

### Meaning Of beta

For AQSM:

```text
beta = 2                 because r = 1
```

The paper defines:

```text
beta = 2, if r = 1
beta = r, if r > 1
```

So for this example:

```text
beta = 2
```

`beta` is a helper parameter used only to compute `alpha`. The special case `r = 1 -> beta = 2` prevents the `alpha` formula from producing an unusable fractional or negative count.

### Meaning Of alpha

The paper defines:

```text
alpha = 2^(2*beta - 3) - 1
      = 2^(2*2 - 3) - 1
      = 2^1 - 1
      = 1
```

In AQSM, `alpha` controls how many block sets are selected from lower-priority and higher-priority bit-plane groups.

The paper says:

```text
number of low-half block sets  = alpha
number of high-half block sets = alpha + 2
```

For this example:

```text
low-half block sets  = alpha     = 1
high-half block sets = alpha + 2 = 3
total block sets     = 1 + 3     = 4
```

Each block set contains 4 binary blocks. Therefore:

```text
total binary blocks entering QBA = 4 block sets * 4 blocks each = 16 blocks
```

For `r = 1`, these blocks are arranged into four possible `4x4` AQSM outputs, but the watermarking scheme only embeds three of them.

### Meaning Of d

The paper defines the QBA level used for embedding as:

```text
d = 1, if r = 1
d = r, if r > 1
```

Therefore:

```text
d = 1
```

`d` is the aggregation depth. One QBA level means:

```text
four 2x2 blocks -> one 4x4 block
```

That is exactly what we need here, because the watermark bit planes are `2x2` and the carrier is `4x4`.

If `d = 2`, QBA would mean two rounds of aggregation:

```text
sixteen 2x2 blocks -> four 4x4 blocks -> one 8x8 block
```

But this example does not use `d = 2`.

### Meaning Of q

The paper defines:

```text
q = 4, if r = 1
q = 4^(r-d), if r > 1
```

So:

```text
q = 4
```

`q` is the number of AQSM binary watermark images after QBA at level `d`.

For this `r = 1` example, AQSM can produce four `4x4` binary images:

```text
Wstar1, Wstar2, Wstar3, Wstar4
```

However, the paper explicitly says that only three are actually embedded for `r = 1`, because the scheme embeds into the first three LSB planes of the carrier:

```text
embedded:
Wstar1 -> first LSB plane, bit0
Wstar2 -> second LSB plane, bit1
Wstar3 -> third LSB plane, bit2

not embedded:
Wstar4
```

The paper does not state the exact content of the omitted fourth `r = 1` AQSM output.

### Summary For This Example

All parameters for the worked example are:

```text
m     = 1    watermark side length is 2^1 = 2
n     = 2    carrier side length is 2^2 = 4
r     = 1    carrier side is 2^1 times larger than watermark side
beta  = 2    helper value required by AQSM for r = 1
alpha = 1    controls the number of selected AQSM block sets
d     = 1    one QBA aggregation level: 2x2 blocks become 4x4 blocks
q     = 4    AQSM produces four outputs, but only three are embedded
```

The paper then states that, for `r = 1`, only three of those four AQSM outputs are embedded because of limited LSB space.

## Step 3: Compute Histogram Parameters

The watermark pixel values are:

```text
130, 200, 170, 255
```

Dark interval is `0..127`. Bright interval is `128..255`.

So:

```text
H(127) = number of watermark pixels <= 127 = 0
```

Using the natural watermark-pixel denominator:

```text
T_dark   = H(127) / 4 = 0 / 4 = 0
T_bright = 1 - T_dark = 1
```

Using the paper's printed denominator for this tiny case, `2^m x 2^n = 2 x 4 = 8`:

```text
T_dark   = H(127) / 8 = 0 / 8 = 0
T_bright = 1 - T_dark = 1
```

So the ambiguity does not affect this example.

The paper sets:

```text
lambda = 0.5
```

Then:

```text
|T_bright - T_dark| = |1 - 0| = 1
```

Since:

```text
1 >= lambda
```

we get:

```text
tau1 = 1
```

For `tau2`, compare the dominant side against:

```text
(1 + lambda) / 2 = (1 + 0.5) / 2 = 0.75
```

Since:

```text
T_bright = 1 >= 0.75
```

we get:

```text
tau2 = 1
```

Therefore, this example uses the HDWM branch:

```text
b_prime = w xor (1 - V)
w_hat   = b_prime xor (1 - V)
```

## Step 4: Decompose The Watermark Into Bit Planes

Using `w1 = b0`, ..., `w8 = b7`:

```text
w1, weight 1:
[[0, 0],
 [0, 1]]

w2, weight 2:
[[1, 0],
 [1, 1]]

w3, weight 4:
[[0, 0],
 [0, 1]]

w4, weight 8:
[[0, 1],
 [1, 1]]

w5, weight 16:
[[0, 0],
 [0, 1]]

w6, weight 32:
[[0, 0],
 [1, 1]]

w7, weight 64:
[[0, 1],
 [0, 1]]

w8, weight 128:
[[1, 1],
 [1, 1]]
```

You can verify one pixel:

```text
W[0,0] = 130 = 10000010

b7 b6 b5 b4 b3 b2 b1 b0
 1  0  0  0  0  0  1  0

So at [0,0]:
w8 = 1, w7 = 0, w6 = 0, w5 = 0, w4 = 0, w3 = 0, w2 = 1, w1 = 0
```

## Step 5: Build The AQSM Watermarks With QBA

QBA combines four `2x2` binary blocks into one `4x4` binary block:

```text
QBA(A, B, C, D) =
[[A top row, B top row],
 [A bot row, B bot row],
 [C top row, D top row],
 [C bot row, D bot row]]
```

Equivalently:

```text
top-left     = A
top-right    = B
bottom-left  = C
bottom-right = D
```

For `r = 1`, the paper embeds these three QBA outputs.

### AQSM Watermark 1

```text
Wstar1 = QBA(w1, w2, w3, w4)
```

So:

```text
Wstar1 =
[[0, 0, 1, 0],
 [0, 1, 1, 1],
 [0, 0, 0, 1],
 [0, 1, 1, 1]]
```

### AQSM Watermark 2

```text
Wstar2 = QBA(w5, w7, w7, w7)
```

So:

```text
Wstar2 =
[[0, 0, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1]]
```

### AQSM Watermark 3

```text
Wstar3 = QBA(w6, w8, w8, w8)
```

So:

```text
Wstar3 =
[[0, 0, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1]]
```

## Step 6: Compute The Carrier MSB Xor Matrix

For `r = 1`:

```text
eta = 0
V = b7 xor b6 xor b5
```

Example for `C[0,0] = 212`:

```text
212 = 11010100
b7 b6 b5 = 1, 1, 0
V = 1 xor 1 xor 0 = 0
```

Doing this for every carrier pixel gives:

```text
V =
[[0, 1, 1, 1],
 [0, 0, 1, 1],
 [0, 1, 1, 1],
 [1, 0, 0, 0]]
```

## Step 7: Embed Wstar1 Into The First LSB Plane

This is carrier bit plane `p = 0`.

Because `tau1 = 1` and `tau2 = 1`:

```text
target bit = b_prime = Wstar1 xor (1 - V)
```

Original carrier first LSB plane:

```text
C bit0 =
[[0, 1, 1, 0],
 [1, 0, 0, 1],
 [0, 1, 1, 0],
 [0, 1, 0, 1]]
```

Target first LSB plane:

```text
target bit0 =
[[1, 0, 1, 0],
 [1, 0, 1, 1],
 [1, 0, 0, 1],
 [0, 0, 0, 0]]
```

After setting bit0 to this target:

```text
C_after_bit0 =
[[213,  46, 133,  88],
 [ 17, 190,  65, 251],
 [103,  72, 154,  37],
 [240, 120,  12, 200]]
```

One pixel check:

```text
C[0,0] = 212 = 11010100
V[0,0] = 0
Wstar1[0,0] = 0

b_prime = 0 xor (1 - 0) = 1

Set bit0 to 1:
11010100 -> 11010101 = 213
```

## Step 8: Embed Wstar2 Into The Second LSB Plane

This is carrier bit plane `p = 1`.

```text
target bit = b_prime = Wstar2 xor (1 - V)
```

Original second LSB plane after step 7:

```text
bit1 =
[[0, 1, 0, 0],
 [0, 1, 0, 1],
 [1, 0, 1, 0],
 [0, 0, 0, 0]]
```

Target second LSB plane:

```text
target bit1 =
[[1, 0, 0, 1],
 [1, 0, 0, 1],
 [1, 1, 0, 1],
 [0, 0, 1, 0]]
```

After setting bit1:

```text
C_after_bit1 =
[[215,  44, 133,  90],
 [ 19, 188,  65, 251],
 [103,  74, 152,  39],
 [240, 120,  14, 200]]
```

## Step 9: Embed Wstar3 Into The Third LSB Plane

This is carrier bit plane `p = 2`.

```text
target bit = b_prime = Wstar3 xor (1 - V)
```

Original third LSB plane after step 8:

```text
bit2 =
[[1, 1, 1, 0],
 [0, 1, 0, 0],
 [1, 0, 0, 1],
 [0, 0, 1, 0]]
```

Target third LSB plane:

```text
target bit2 =
[[1, 0, 1, 1],
 [0, 0, 1, 1],
 [0, 1, 1, 1],
 [1, 0, 0, 0]]
```

After setting bit2, the final watermarked carrier is:

```text
CW =
[[215,  40, 133,  94],
 [ 19, 184,  69, 255],
 [ 99,  78, 156,  39],
 [244, 120,  10, 200]]
```

Binary form:

```text
[[11010111, 00101000, 10000101, 01011110],
 [00010011, 10111000, 01000101, 11111111],
 [01100011, 01001110, 10011100, 00100111],
 [11110100, 01111000, 00001010, 11001000]]
```

## Step 10: Extract The Three AQSM Watermarks

Extraction uses the same `V` matrix. The carrier MSBs did not change because only bit planes `0`, `1`, and `2` were modified.

For this example:

```text
w_hat = b_prime xor (1 - V)
```

### Extract From First LSB

```text
E1 =
[[0, 0, 1, 0],
 [0, 1, 1, 1],
 [0, 0, 0, 1],
 [0, 1, 1, 1]]
```

This equals `Wstar1`.

### Extract From Second LSB

```text
E2 =
[[0, 0, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1]]
```

This equals `Wstar2`.

### Extract From Third LSB

```text
E3 =
[[0, 0, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1]]
```

This equals `Wstar3`.

## Step 11: Apply Inverse QBA

Inverse QBA splits each `4x4` extracted binary image into four `2x2` blocks:

```text
top-left, top-right, bottom-left, bottom-right
```

### Inverse QBA Of E1

```text
E1 blocks =

B1.1 =
[[0, 0],
 [0, 1]]

B1.2 =
[[1, 0],
 [1, 1]]

B1.3 =
[[0, 0],
 [0, 1]]

B1.4 =
[[0, 1],
 [1, 1]]
```

Since:

```text
E1 = QBA(w1, w2, w3, w4)
```

we recover:

```text
w1 = B1.1
w2 = B1.2
w3 = B1.3
w4 = B1.4
```

### Inverse QBA Of E2

```text
E2 blocks =

B2.1 =
[[0, 0],
 [0, 1]]

B2.2 =
[[0, 1],
 [0, 1]]

B2.3 =
[[0, 1],
 [0, 1]]

B2.4 =
[[0, 1],
 [0, 1]]
```

Since:

```text
E2 = QBA(w5, w7, w7, w7)
```

we recover:

```text
w5 = B2.1
w7 candidates = B2.2, B2.3, B2.4
```

### Inverse QBA Of E3

```text
E3 blocks =

B3.1 =
[[0, 0],
 [1, 1]]

B3.2 =
[[1, 1],
 [1, 1]]

B3.3 =
[[1, 1],
 [1, 1]]

B3.4 =
[[1, 1],
 [1, 1]]
```

Since:

```text
E3 = QBA(w6, w8, w8, w8)
```

we recover:

```text
w6 = B3.1
w8 candidates = B3.2, B3.3, B3.4
```

## Step 12: Apply Quantum Refining As Majority Vote

The paper's quantum refining chooses the majority value from an odd sequence of qubits.

For a classical matrix implementation, this means pixel-wise majority voting over repeated copies.

For three binary copies `A`, `B`, `C`:

```text
majority(A, B, C)[y,x] = 1 if A[y,x] + B[y,x] + C[y,x] >= 2
                         0 otherwise
```

In this no-attack example, the repeated copies are already identical.

So:

```text
w7 = majority(B2.2, B2.3, B2.4)
   =
[[0, 1],
 [0, 1]]

w8 = majority(B3.2, B3.3, B3.4)
   =
[[1, 1],
 [1, 1]]
```

The full recovered bit-plane set is:

```text
w1 =
[[0, 0],
 [0, 1]]

w2 =
[[1, 0],
 [1, 1]]

w3 =
[[0, 0],
 [0, 1]]

w4 =
[[0, 1],
 [1, 1]]

w5 =
[[0, 0],
 [0, 1]]

w6 =
[[0, 0],
 [1, 1]]

w7 =
[[0, 1],
 [0, 1]]

w8 =
[[1, 1],
 [1, 1]]
```

## Step 13: Reconstruct The Grayscale Watermark

Use the bit-plane weights:

```text
W_rec = 1*w1
      + 2*w2
      + 4*w3
      + 8*w4
      + 16*w5
      + 32*w6
      + 64*w7
      + 128*w8
```

Pixel `[0,0]`:

```text
w1=0, w2=1, w3=0, w4=0, w5=0, w6=0, w7=0, w8=1

value = 0*1 + 1*2 + 0*4 + 0*8 + 0*16 + 0*32 + 0*64 + 1*128
      = 130
```

Pixel `[0,1]`:

```text
w1=0, w2=0, w3=0, w4=1, w5=0, w6=0, w7=1, w8=1

value = 0 + 0 + 0 + 8 + 0 + 0 + 64 + 128
      = 200
```

Pixel `[1,0]`:

```text
w1=0, w2=1, w3=0, w4=1, w5=0, w6=1, w7=0, w8=1

value = 0 + 2 + 0 + 8 + 0 + 32 + 0 + 128
      = 170
```

Pixel `[1,1]`:

```text
w1=1, w2=1, w3=1, w4=1, w5=1, w6=1, w7=1, w8=1

value = 1 + 2 + 4 + 8 + 16 + 32 + 64 + 128
      = 255
```

Therefore:

```text
W_rec =
[[130, 200],
 [170, 255]]
```

This exactly matches the original watermark:

```text
W_rec == W
```

## Step 14: Toy Attack Simulation

The clean extraction above proves the embedding/extraction equations are internally consistent, but it does not test robustness.

The paper's experiments attack large `512x512` watermarked images with random salt-and-pepper noise and cropping. A `4x4` carrier is too small to reproduce those statistical experiments meaningfully. Here, we do a deterministic toy attack that is still mathematically concrete and code-ready:

```text
Pepper one watermarked carrier pixel:
CW[0,2] = 133  ->  0
```

This is a salt-and-pepper style attack because the attacked pixel is forced to one endpoint of the grayscale range. On a `4x4` image, one attacked pixel is already `1/16 = 6.25%` of the carrier image.

The attacked watermarked carrier is:

```text
CW_attack =
[[215,  40,   0,  94],
 [ 19, 184,  69, 255],
 [ 99,  78, 156,  39],
 [244, 120,  10, 200]]
```

Binary form:

```text
[[11010111, 00101000, 00000000, 01011110],
 [00010011, 10111000, 01000101, 11111111],
 [01100011, 01001110, 10011100, 00100111],
 [11110100, 01111000, 00001010, 11001000]]
```

### Recompute V After The Attack

The extraction process computes `V = b7 xor b6 xor b5` from the image being extracted.

Only pixel `[0,2]` changed:

```text
before attack: CW[0,2] = 133 = 10000101
V_before = 1 xor 0 xor 0 = 1

after attack: CW_attack[0,2] = 0 = 00000000
V_after = 0 xor 0 xor 0 = 0
```

So the attacked `V` matrix is:

```text
V_attack =
[[0, 1, 0, 1],
 [0, 0, 1, 1],
 [0, 1, 1, 1],
 [1, 0, 0, 0]]
```

### Extract From The Attacked Image

The branch is still:

```text
w_hat = b_prime xor (1 - V_attack)
```

Extracted first AQSM image:

```text
E1_attack =
[[0, 0, 1, 0],
 [0, 1, 1, 1],
 [0, 0, 0, 1],
 [0, 1, 1, 1]]
```

This still equals `Wstar1`.

Extracted second AQSM image:

```text
E2_attack =
[[0, 0, 1, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1]]
```

Compare that with the clean `Wstar2`:

```text
Wstar2 =
[[0, 0, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1]]
```

The attack changed exactly one extracted AQSM bit:

```text
E2_attack[0,2] changed from 0 to 1
```

Extracted third AQSM image:

```text
E3_attack =
[[0, 0, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1]]
```

This still equals `Wstar3`.

### Inverse QBA Shows Where The Error Went

Recall:

```text
E2 = QBA(w5, w7, w7, w7)
```

So after inverse QBA, the three repeated `w7` candidates are the top-right, bottom-left, and bottom-right blocks.

For the attacked `E2_attack`:

```text
B2.1 =
[[0, 0],
 [0, 1]]

B2.2 =
[[1, 1],
 [0, 1]]

B2.3 =
[[0, 1],
 [0, 1]]

B2.4 =
[[0, 1],
 [0, 1]]
```

Here:

```text
w5 = B2.1
w7 candidates = B2.2, B2.3, B2.4
```

Only `B2.2[0,0]` is wrong. The other two repeated copies still contain the correct value.

### Majority Vote Corrects The Repeated Plane

At position `[0,0]`, the three `w7` candidate values are:

```text
B2.2[0,0] = 1
B2.3[0,0] = 0
B2.4[0,0] = 0
```

The majority is:

```text
majority(1, 0, 0) = 0
```

Therefore:

```text
w7_recovered =
[[0, 1],
 [0, 1]]
```

which matches the original `w7`.

The reconstructed watermark after this toy attack is still:

```text
W_rec_attack =
[[130, 200],
 [170, 255]]
```

So for this specific attacked pixel:

```text
W_rec_attack == W
```

### What This Attack Simulation Does And Does Not Prove

It proves:

- the extraction equations can be run on an attacked watermarked image
- a concrete pepper-noise corruption can produce an extracted AQSM bit error
- AQSM's repeated high-plane data plus majority voting can correct that bit error
- the original `2x2` watermark is exactly recovered in this selected toy attack

It does not prove:

- the paper's reported PSNR/NCC values
- robustness over random salt-and-pepper noise
- robustness over cropping
- robustness for all one-pixel attacks on a `4x4` carrier

Some `4x4` one-pixel attacks damage non-repeated low bit planes, which this `r = 1` setup cannot always correct. The paper's robustness claim is statistical and experimental; reproducing it properly requires larger images, random attack trials, and PSNR/NCC evaluation.

## Implementation Skeleton

This is not a full program, but it is the direct structure needed for code.

```python
def bit_plane(image, p):
    return [[(pixel >> p) & 1 for pixel in row] for row in image]

def qba(A, B, C, D):
    h = len(A)
    return [A[y] + B[y] for y in range(h)] + [C[y] + D[y] for y in range(h)]

def inverse_qba(M):
    h = len(M) // 2
    w = len(M[0]) // 2
    return (
        [row[:w] for row in M[:h]],
        [row[w:] for row in M[:h]],
        [row[:w] for row in M[h:]],
        [row[w:] for row in M[h:]],
    )

def majority3(A, B, C):
    h = len(A)
    w = len(A[0])
    return [
        [1 if A[y][x] + B[y][x] + C[y][x] >= 2 else 0 for x in range(w)]
        for y in range(h)
    ]

def v_eta_r1(pixel):
    b7 = (pixel >> 7) & 1
    b6 = (pixel >> 6) & 1
    b5 = (pixel >> 5) & 1
    return b7 ^ b6 ^ b5

def hdwm_embed_bit(w, V, tau1, tau2):
    if tau1 == 0:
        return w
    if tau2 == 0:
        return w ^ V
    return w ^ (1 - V)

def hdwm_extract_bit(b_prime, V, tau1, tau2):
    if tau1 == 0:
        return b_prime
    if tau2 == 0:
        return b_prime ^ V
    return b_prime ^ (1 - V)

def set_bit(pixel, p, bit):
    return (pixel & ~(1 << p)) | (bit << p)
```

## Second-Pass Validity Review

I rechecked the walkthrough against the paper/source and `paper_analysis.md`.

Valid parts:

- The example uses `r = 1`, where the paper explicitly provides the three embedded AQSM block sets.
- The `beta`, `alpha`, `d`, and `q` values follow the paper's formulas.
- QBA and inverse QBA are direct block placement/splitting operations.
- The simplified HDWM formulas match the embedding and extraction tables in the paper.
- The example avoids relying on the unresolved histogram denominator issue because `H(127) = 0` gives the same `tau1 = 1`, `tau2 = 1` under both denominators.
- The extracted bit planes reconstruct the original watermark exactly.
- The added toy attack simulation is valid for the selected attacked pixel: it corrupts one repeated `w7` copy and majority voting restores the original watermark.

Remaining unresolved paper issues:

- The exact AQSM customization schedule for larger scale factors, especially `r = 3`, is not fully specified in the paper.
- The paper states that AQSM outputs four binary images for `r = 1`, but only three are embedded; the unembedded fourth output is not needed for this example.
- The paper describes `V_eta` as the xor of 3 or 4 MSBs but does not write a formal bit-index formula. This note uses the natural 8-bit convention: `b7 xor b6 xor b5` for the 3-MSB case.
- The histogram denominator should be clarified before implementing a general reproduction of the paper's experiments.

Conclusion:

This `2x2 -> 4x4` walkthrough is mathematically consistent, follows the parts of the paper that are explicit, and is directly translatable into code. It should not be treated as a complete specification for all `r` values until the unresolved paper ambiguities are clarified.
