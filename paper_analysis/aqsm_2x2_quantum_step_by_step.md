# AQSM/HDWM Worked Example With Quantum-State Notation

This is a quantum-mathematical companion to `aqsm_2x2_step_by_step.md`.

It uses the same example:

- watermark image: `2x2`
- carrier image: `4x4`
- scale factor: `r = 1`
- grayscale depth: 8 bits

The goal is to keep the paper's quantum notation visible while still making every step implementable.

## Sources Checked

- Local paper: `adaptive quantum scaling model.pdf`
- Local source: `arxiv_src/A3_Manuscript.tex`
- Existing walkthrough: `aqsm_2x2_step_by_step.md`

Relevant paper locations:

- NEQR definition: `arxiv_src/A3_Manuscript.tex`, lines 110-115
- AQSM and QBA definition: lines 117-161
- HDWM histogram parameters: lines 168-198
- `eta` and `V_eta`: lines 201-210
- watermark/carrier NEQR states for embedding: lines 221-228
- explicit `r = 1` AQSM sets: line 245
- HDWM embedding Table I: lines 250-271
- HDWM extraction Table II and refining: lines 289-326

## Important Scope

This file does not invent a full gate-level implementation beyond what the paper specifies.

The paper gives circuit figures for QBS, QIB, embedding, extraction, and refining, but the text does not fully specify every gate-level detail needed to reconstruct a complete scalable circuit from scratch. Therefore, this walkthrough uses:

- NEQR quantum states
- computational-basis bit registers
- logical transformations matching the paper's tables
- explicit warnings where a step is a basis-state update rather than a derived unitary circuit

This mirrors the paper's own experiment style: the experiments are MATLAB simulations using matrices, not runs on quantum hardware.

## Step 1: Choose The Same Input Images

Watermark image:

```text
W =
[[130, 200],
 [170, 255]]
```

Binary:

```text
130 = 10000010
200 = 11001000
170 = 10101010
255 = 11111111
```

Carrier image:

```text
C =
[[212,  47, 133,  88],
 [ 17, 190,  64, 251],
 [102,  73, 155,  36],
 [240, 121,  12, 201]]
```

Binary:

```text
[[11010100, 00101111, 10000101, 01011000],
 [00010001, 10111110, 01000000, 11111011],
 [01100110, 01001001, 10011011, 00100100],
 [11110000, 01111001, 00001100, 11001001]]
```

## Step 2: Register And Bit Conventions

Use 8 grayscale qubits:

```text
|g7 g6 g5 g4 g3 g2 g1 g0>
```

where:

```text
g7 = most significant bit, weight 128
g6 = weight 64
g5 = weight 32
g4 = weight 16
g3 = weight 8
g2 = weight 4
g1 = weight 2
g0 = least significant bit, weight 1
```

To match the paper's watermark bit-plane notation:

```text
w1 = g0
w2 = g1
w3 = g2
w4 = g3
w5 = g4
w6 = g5
w7 = g6
w8 = g7
```

For the watermark coordinates:

```text
2x2 image -> one Y qubit and one X qubit
|YX> in {|00>, |01>, |10>, |11>}
```

For the carrier coordinates:

```text
4x4 image -> two Y qubits and two X qubits
|YX> = |Y1 Y0 X1 X0>
```

Example:

```text
carrier coordinate row 2, column 3:
Y = 2 = 10
X = 3 = 11
|YX> = |1011>
```

## Step 3: NEQR Encoding Of The Watermark

The paper's NEQR form is:

```text
|I> = (1 / 2^s) * sum_Y sum_X |C(Y,X)>|YX>
```

for a `2^s x 2^s` image.

Our watermark is `2x2 = 2^1 x 2^1`, so:

```text
s = m = 1
normalization factor = 1 / 2
```

The watermark NEQR state is:

```text
|W> = 1/2 * (
    |10000010>|00>
  + |11001000>|01>
  + |10101010>|10>
  + |11111111>|11>
)
```

This means:

```text
|10000010>|00> represents W[0,0] = 130
|11001000>|01> represents W[0,1] = 200
|10101010>|10> represents W[1,0] = 170
|11111111>|11> represents W[1,1] = 255
```

Qubit count:

```text
8 grayscale qubits + 1 Y qubit + 1 X qubit = 10 qubits
```

## Step 4: NEQR Encoding Of The Carrier

The carrier is `4x4 = 2^2 x 2^2`, so:

```text
s = n = 2
normalization factor = 1 / 4
```

The carrier NEQR state is:

```text
|C> = 1/4 * (
    |11010100>|0000> + |00101111>|0001> + |10000101>|0010> + |01011000>|0011>
  + |00010001>|0100> + |10111110>|0101> + |01000000>|0110> + |11111011>|0111>
  + |01100110>|1000> + |01001001>|1001> + |10011011>|1010> + |00100100>|1011>
  + |11110000>|1100> + |01111001>|1101> + |00001100>|1110> + |11001001>|1111>
)
```

Each coordinate ket is:

```text
|Y1 Y0 X1 X0>
```

Example:

```text
|00100100>|1011>
```

means:

```text
pixel value = 00100100 = 36
Y = 10 = row 2
X = 11 = column 3
```

Qubit count:

```text
8 grayscale qubits + 2 Y qubits + 2 X qubits = 12 qubits
```

## Step 5: Compute The Scale Parameters

The paper defines:

```text
watermark size = 2^m x 2^m
carrier size   = 2^n x 2^n
r = n - m
```

For this example:

```text
watermark = 2x2 -> m = 1
carrier   = 4x4 -> n = 2
r = n - m = 2 - 1 = 1
```

The AQSM helper parameter is:

```text
beta = 2, if r = 1
beta = r, if r > 1
```

So:

```text
beta = 2
```

The paper defines:

```text
alpha = 2^(2*beta - 3) - 1
```

Therefore:

```text
alpha = 2^(2*2 - 3) - 1
      = 2^1 - 1
      = 1
```

For embedding, the paper sets:

```text
d = 1, if r = 1
d = r, if r > 1
```

So:

```text
d = 1
```

The paper defines the number of AQSM outputs:

```text
q = 4, if r = 1
q = 4^(r-d), if r > 1
```

So:

```text
q = 4
```

For `r = 1`, the paper explicitly says AQSM outputs four binary images, but only three are embedded.

## Step 6: Compute HDWM Histogram Parameters

The paper defines:

```text
h(g) = number of watermark pixels with grayscale value g
H(g) = sum from x = 0 to g of h(x)
```

The dark interval is:

```text
0..127
```

The bright interval is:

```text
128..255
```

Our watermark values are:

```text
130, 200, 170, 255
```

All are bright.

So:

```text
H(127) = 0
```

The paper prints:

```text
T_dark   = H(127) / (2^m * 2^n)
T_bright = 1 - H(127) / (2^m * 2^n)
```

A watermark of size `2^m x 2^m` would naturally use denominator `2^(2m)`. This is an ambiguity in the paper.

For this example, the ambiguity does not affect the branch:

```text
H(127) = 0
```

So either denominator gives:

```text
T_dark = 0
T_bright = 1
```

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
1 >= 0.5
```

we get:

```text
tau1 = 1
```

For `tau2`, compare to:

```text
(1 + lambda) / 2 = 0.75
```

Since:

```text
T_bright = 1 >= 0.75
```

we get:

```text
tau2 = 1
```

So this example uses the HDWM branch:

```text
embedded LSB bit = watermark bit xor (1 - V)
extracted bit    = embedded LSB bit xor (1 - V)
```

## Step 7: Decompose |W> Into Binary Bit-Plane States

The paper says AQSM preparation is achieved by bit-plane decomposition.

In quantum-state notation, each bit plane can be represented as a binary quantum image:

```text
|wi> = 1/2 * sum_y sum_x |wi(y,x)>|yx>
```

Each `|wi(y,x)>` is one qubit, either `|0>` or `|1>`.

Important no-cloning note:

The paper says the bit decomposition must be repeated `alpha + 2` times because an unknown quantum state cannot be copied. In this walkthrough, we write the resulting bit-plane states explicitly from the known input image. That is fine for mathematical explanation and classical simulation, but it should not be mistaken for cloning an unknown quantum state.

The bit-plane states are:

```text
|w1> = 1/2 * ( |0>|00> + |0>|01> + |0>|10> + |1>|11> )
|w2> = 1/2 * ( |1>|00> + |0>|01> + |1>|10> + |1>|11> )
|w3> = 1/2 * ( |0>|00> + |0>|01> + |0>|10> + |1>|11> )
|w4> = 1/2 * ( |0>|00> + |1>|01> + |1>|10> + |1>|11> )
|w5> = 1/2 * ( |0>|00> + |0>|01> + |0>|10> + |1>|11> )
|w6> = 1/2 * ( |0>|00> + |0>|01> + |1>|10> + |1>|11> )
|w7> = 1/2 * ( |0>|00> + |1>|01> + |0>|10> + |1>|11> )
|w8> = 1/2 * ( |1>|00> + |1>|01> + |1>|10> + |1>|11> )
```

Matrix view of the same states:

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

## Step 8: Define QBA As A Quantum Coordinate-Splicing Rule

The paper's QBA/QBS combines four equal-size binary blocks into one larger binary image.

For four `2x2` binary images:

```text
A, B, C, D
```

QBA produces one `4x4` binary image:

```text
QBA(A, B, C, D) =
[A | B]
[C | D]
```

In quantum coordinate notation:

```text
|QBA(A,B,C,D)> = 1/4 * sum_Y sum_X |q(Y,X)>|YX>
```

where the output coordinate is:

```text
|YX> = |Y1 Y0 X1 X0>
```

The high coordinate bits choose the quadrant:

```text
Y1 X1 = 00 -> use A at local coordinate |Y0 X0>
Y1 X1 = 01 -> use B at local coordinate |Y0 X0>
Y1 X1 = 10 -> use C at local coordinate |Y0 X0>
Y1 X1 = 11 -> use D at local coordinate |Y0 X0>
```

This is the mathematical version of the paper's QBS placement into coordinates `00`, `01`, `10`, and `11`.

## Step 9: Build The Three Embedded AQSM States

The paper explicitly states that for `r = 1`, the three embedded AQSM watermarks are obtained from:

```text
{w1, w2, w3, w4}
{w5, w7, w7, w7}
{w6, w8, w8, w8}
```

Therefore:

```text
|W*_1> = QBA(|w1>, |w2>, |w3>, |w4>)
|W*_2> = QBA(|w5>, |w7>, |w7>, |w7>)
|W*_3> = QBA(|w6>, |w8>, |w8>, |w8>)
```

The paper also says there are four AQSM outputs for `r = 1`, but only three are embedded. The omitted fourth output is not explicitly specified in the paper, so it is not used here.

The state form is:

```text
|W*_j> = 1/4 * sum_Y sum_X |W*_j(Y,X)>|YX>
```

The three binary images are:

```text
W*_1 =
[[0, 0, 1, 0],
 [0, 1, 1, 1],
 [0, 0, 0, 1],
 [0, 1, 1, 1]]
```

```text
W*_2 =
[[0, 0, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1]]
```

```text
W*_3 =
[[0, 0, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1]]
```

These are quantum binary images because each matrix defines all amplitudes in:

```text
1/4 * sum_Y sum_X |bit>|YX>
```

## Step 10: Compute V_eta From The Carrier State

The paper defines `eta` as:

```text
eta = 0, if r = 1
eta = r mod 2, if r > 1
```

Since:

```text
r = 1
```

we have:

```text
eta = 0
```

The paper says that when `eta = 0`, embedding uses the XOR result of 3 MSBs.

The paper does not explicitly name the bit indices. For an 8-bit pixel, the natural interpretation is:

```text
V(Y,X) = c7(Y,X) xor c6(Y,X) xor c5(Y,X)
```

At the quantum-register level, this can be represented as computing a parity bit into an ancilla:

```text
|c7 c6 c5 ... c0>|0>_v
    -> |c7 c6 c5 ... c0>|c7 xor c6 xor c5>_v
```

For the carrier matrix, this gives:

```text
V =
[[0, 1, 1, 1],
 [0, 0, 1, 1],
 [0, 1, 1, 1],
 [1, 0, 0, 0]]
```

Example:

```text
C[0,0] = 212 = 11010100
c7 c6 c5 = 1, 1, 0
V(0,0) = 1 xor 1 xor 0 = 0
```

## Step 11: Express HDWM Embedding As A Basis-State Update

The paper's Table I gives flip/no-change rules for the selected carrier LSB.

For our branch:

```text
tau1 = 1
tau2 = 1
```

Table I is equivalent to:

```text
target_j(Y,X) = W*_j(Y,X) xor (1 - V(Y,X))
```

where:

```text
j = 1 -> embed into carrier bit0
j = 2 -> embed into carrier bit1
j = 3 -> embed into carrier bit2
```

Important circuit note:

Table I tells us the desired logical update of the carrier LSB. This walkthrough uses that table-level update to define the output state. A complete strictly unitary circuit would need to preserve reversibility with suitable workspace or use the paper's circuit construction. The paper gives the embedding circuit as a figure, but the text does not provide enough detail here to derive every gate in this note without guessing.

The target bit planes are:

```text
target bit0 = W*_1 xor (1 - V)
=
[[1, 0, 1, 0],
 [1, 0, 1, 1],
 [1, 0, 0, 1],
 [0, 0, 0, 0]]
```

```text
target bit1 = W*_2 xor (1 - V)
=
[[1, 0, 0, 1],
 [1, 0, 0, 1],
 [1, 1, 0, 1],
 [0, 0, 1, 0]]
```

```text
target bit2 = W*_3 xor (1 - V)
=
[[1, 0, 1, 1],
 [0, 0, 1, 1],
 [0, 1, 1, 1],
 [1, 0, 0, 0]]
```

The watermarked carrier bits are:

```text
c0' = target bit0
c1' = target bit1
c2' = target bit2
c3' = c3
c4' = c4
c5' = c5
c6' = c6
c7' = c7
```

So only the first three LSB planes change.

## Step 12: Build The Watermarked Carrier State |CW>

After applying the HDWM table-level update, the watermarked carrier matrix is:

```text
CW =
[[215,  40, 133,  94],
 [ 19, 184,  69, 255],
 [ 99,  78, 156,  39],
 [244, 120,  10, 200]]
```

Binary:

```text
[[11010111, 00101000, 10000101, 01011110],
 [00010011, 10111000, 01000101, 11111111],
 [01100011, 01001110, 10011100, 00100111],
 [11110100, 01111000, 00001010, 11001000]]
```

Therefore the NEQR state is:

```text
|CW> = 1/4 * (
    |11010111>|0000> + |00101000>|0001> + |10000101>|0010> + |01011110>|0011>
  + |00010011>|0100> + |10111000>|0101> + |01000101>|0110> + |11111111>|0111>
  + |01100011>|1000> + |01001110>|1001> + |10011100>|1010> + |00100111>|1011>
  + |11110100>|1100> + |01111000>|1101> + |00001010>|1110> + |11001000>|1111>
)
```

One pixel check:

```text
C[0,0] = 212 = 11010100
V(0,0) = 0
W*_1(0,0) = 0
W*_2(0,0) = 0
W*_3(0,0) = 0

target bit0 = 0 xor (1 - 0) = 1
target bit1 = 0 xor (1 - 0) = 1
target bit2 = 0 xor (1 - 0) = 1

Original low bits: 100
New low bits:      111

11010100 -> 11010111 = 215
```

## Step 13: Extract The AQSM States From |CW>

The paper's extraction process starts from the watermarked image represented again by NEQR.

For this branch:

```text
tau1 = 1
tau2 = 1
```

Table II is equivalent to:

```text
E_j(Y,X) = selected_LSB_j(Y,X) xor (1 - V(Y,X))
```

Since only LSBs changed, the MSBs are the same as before, so `V` is:

```text
V =
[[0, 1, 1, 1],
 [0, 0, 1, 1],
 [0, 1, 1, 1],
 [1, 0, 0, 0]]
```

The extracted binary quantum images are:

```text
|E_j> = 1/4 * sum_Y sum_X |E_j(Y,X)>|YX>
```

For `j = 1`:

```text
E1 =
[[0, 0, 1, 0],
 [0, 1, 1, 1],
 [0, 0, 0, 1],
 [0, 1, 1, 1]]
```

So:

```text
E1 = W*_1
```

For `j = 2`:

```text
E2 =
[[0, 0, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1]]
```

So:

```text
E2 = W*_2
```

For `j = 3`:

```text
E3 =
[[0, 0, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1]]
```

So:

```text
E3 = W*_3
```

## Step 14: Apply Inverse QBA In Quantum Coordinates

Inverse QBA splits a `4x4` binary quantum image into four `2x2` binary quantum images by quadrant.

In coordinate terms:

```text
Y1 X1 = 00 -> top-left block
Y1 X1 = 01 -> top-right block
Y1 X1 = 10 -> bottom-left block
Y1 X1 = 11 -> bottom-right block
```

For `E1`:

```text
E1 = QBA(w1, w2, w3, w4)
```

so inverse QBA gives:

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
```

For `E2`:

```text
E2 = QBA(w5, w7, w7, w7)
```

so inverse QBA gives:

```text
w5 =
[[0, 0],
 [0, 1]]

w7 candidate 1 =
[[0, 1],
 [0, 1]]

w7 candidate 2 =
[[0, 1],
 [0, 1]]

w7 candidate 3 =
[[0, 1],
 [0, 1]]
```

For `E3`:

```text
E3 = QBA(w6, w8, w8, w8)
```

so inverse QBA gives:

```text
w6 =
[[0, 0],
 [1, 1]]

w8 candidate 1 =
[[1, 1],
 [1, 1]]

w8 candidate 2 =
[[1, 1],
 [1, 1]]

w8 candidate 3 =
[[1, 1],
 [1, 1]]
```

## Step 15: Apply Quantum Refining As Majority Logic

The paper says quantum refining finds the majority of an odd sequence of qubits and ignores the minority.

For three candidate qubits:

```text
a, b, c
```

the majority bit is:

```text
Maj(a,b,c) = 1 if a + b + c >= 2
             0 otherwise
```

As a reversible quantum subroutine, this can be computed into an output ancilla:

```text
|a>|b>|c>|0> -> |a>|b>|c>|Maj(a,b,c)>
```

The paper provides a quantum refining circuit figure, but this logical majority equation is the part used in the simulation-level model.

For `w7`:

```text
w7 = Maj(w7 candidate 1, w7 candidate 2, w7 candidate 3)
```

Since all three are identical:

```text
w7 =
[[0, 1],
 [0, 1]]
```

For `w8`:

```text
w8 = Maj(w8 candidate 1, w8 candidate 2, w8 candidate 3)
```

Since all three are identical:

```text
w8 =
[[1, 1],
 [1, 1]]
```

The recovered bit planes are now:

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

## Step 16: Reconstruct The Watermark Quantum State

Reconstruction combines the recovered bit planes into 8-bit grayscale values.

Because:

```text
w1 = g0
w2 = g1
w3 = g2
w4 = g3
w5 = g4
w6 = g5
w7 = g6
w8 = g7
```

the recovered grayscale register is:

```text
|g7 g6 g5 g4 g3 g2 g1 g0>
 =
|w8 w7 w6 w5 w4 w3 w2 w1>
```

Pixel `[0,0]`:

```text
w8 w7 w6 w5 w4 w3 w2 w1 = 1 0 0 0 0 0 1 0
binary = 10000010
decimal = 130
```

Pixel `[0,1]`:

```text
w8 w7 w6 w5 w4 w3 w2 w1 = 1 1 0 0 1 0 0 0
binary = 11001000
decimal = 200
```

Pixel `[1,0]`:

```text
w8 w7 w6 w5 w4 w3 w2 w1 = 1 0 1 0 1 0 1 0
binary = 10101010
decimal = 170
```

Pixel `[1,1]`:

```text
w8 w7 w6 w5 w4 w3 w2 w1 = 1 1 1 1 1 1 1 1
binary = 11111111
decimal = 255
```

So the recovered quantum watermark state is:

```text
|W_rec> = 1/2 * (
    |10000010>|00>
  + |11001000>|01>
  + |10101010>|10>
  + |11111111>|11>
)
```

Therefore:

```text
|W_rec> = |W>
```

At measurement, this corresponds to the classical image:

```text
W_rec =
[[130, 200],
 [170, 255]]
```

## Step 17: Toy Attack In Quantum-State Notation

The paper tests salt-and-pepper noise and cropping after watermarking. In this tiny example, we use the same deterministic toy attack from the classical walkthrough:

```text
CW[0,2] = 133 -> 0
```

This is a pepper-noise style corruption of one coordinate basis term.

This attack is not a unitary quantum gate. It is a noise/corruption channel applied to the watermarked image data, matching the paper's simulation style.

The attacked matrix is:

```text
CW_attack =
[[215,  40,   0,  94],
 [ 19, 184,  69, 255],
 [ 99,  78, 156,  39],
 [244, 120,  10, 200]]
```

The attacked NEQR state is:

```text
|CW_attack> = 1/4 * (
    |11010111>|0000> + |00101000>|0001> + |00000000>|0010> + |01011110>|0011>
  + |00010011>|0100> + |10111000>|0101> + |01000101>|0110> + |11111111>|0111>
  + |01100011>|1000> + |01001110>|1001> + |10011100>|1010> + |00100111>|1011>
  + |11110100>|1100> + |01111000>|1101> + |00001010>|1110> + |11001000>|1111>
)
```

Only the term at coordinate:

```text
|0010>
```

changed:

```text
before: |10000101>|0010>
after:  |00000000>|0010>
```

### Extract After Attack

Recompute `V` from the attacked image:

```text
V_attack =
[[0, 1, 0, 1],
 [0, 0, 1, 1],
 [0, 1, 1, 1],
 [1, 0, 0, 0]]
```

Extracted AQSM images:

```text
E1_attack =
[[0, 0, 1, 0],
 [0, 1, 1, 1],
 [0, 0, 0, 1],
 [0, 1, 1, 1]]
```

```text
E2_attack =
[[0, 0, 1, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1],
 [0, 1, 0, 1]]
```

```text
E3_attack =
[[0, 0, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1],
 [1, 1, 1, 1]]
```

The attack changed one bit in `E2`:

```text
clean E2[0,2]  = 0
attack E2[0,2] = 1
```

### Majority Vote Corrects This Specific Error

Since:

```text
E2 = QBA(w5, w7, w7, w7)
```

the top-right, bottom-left, and bottom-right quadrants are three copies of `w7`.

After the attack, inverse QBA gives:

```text
w7 candidate 1 =
[[1, 1],
 [0, 1]]

w7 candidate 2 =
[[0, 1],
 [0, 1]]

w7 candidate 3 =
[[0, 1],
 [0, 1]]
```

At position `[0,0]`:

```text
candidate values = 1, 0, 0
Maj(1,0,0) = 0
```

So:

```text
w7_recovered =
[[0, 1],
 [0, 1]]
```

The reconstructed attacked watermark is still:

```text
|W_rec_attack> = |W>
```

or classically:

```text
W_rec_attack =
[[130, 200],
 [170, 255]]
```

This proves this selected toy attack is corrected. It does not prove the paper's full statistical robustness claims.

## Implementation Translation

The quantum notation maps directly to code structures:

```text
NEQR grayscale register        -> uint8 pixel value
NEQR coordinate register       -> matrix index (row, column)
binary quantum image |wi>      -> binary matrix for bit plane i
QBA coordinate splicing        -> quadrant concatenation
V_eta parity ancilla           -> xor of carrier MSB bits
HDWM Table I basis update      -> set selected LSB bit to target
Table II extraction            -> xor selected LSB with branch mask
quantum refining majority      -> pixel-wise majority vote
measurement of |W_rec>         -> recovered grayscale matrix
```

Minimal code formulas for this exact branch:

```text
V[y,x] = c7[y,x] xor c6[y,x] xor c5[y,x]

target0[y,x] = W*_1[y,x] xor (1 - V[y,x])
target1[y,x] = W*_2[y,x] xor (1 - V[y,x])
target2[y,x] = W*_3[y,x] xor (1 - V[y,x])

c0'[y,x] = target0[y,x]
c1'[y,x] = target1[y,x]
c2'[y,x] = target2[y,x]
c3'..c7' = c3..c7
```

Extraction:

```text
E1[y,x] = c0'[y,x] xor (1 - V[y,x])
E2[y,x] = c1'[y,x] xor (1 - V[y,x])
E3[y,x] = c2'[y,x] xor (1 - V[y,x])
```

Then:

```text
inverse QBA -> bit-plane candidates
majority vote -> w7 and w8
bit-plane reconstruction -> |W_rec>
```

## Second-Pass Validity Review

Checked against the paper:

- NEQR state form follows the paper's NEQR definition.
- AQSM/QBA follows the paper's preparation, customization, and aggregation description.
- The `r = 1` AQSM sets are exactly the three sets explicitly listed by the paper.
- `tau1 = 1`, `tau2 = 1` follows the paper's histogram equations for this all-bright watermark.
- `eta = 0` follows the paper because `r = 1`.
- `V = c7 xor c6 xor c5` is the natural interpretation of the paper's "XOR result of 3 MSBs"; the paper does not write the explicit bit indices.
- The HDWM embedding and extraction equations are derived from Table I and Table II.
- The extraction reconstructs the original quantum watermark state exactly in the clean case.
- The toy pepper attack reproduces the same correction behavior as the first walkthrough: one repeated `w7` copy is wrong, and majority vote restores it.

Open issues not invented here:

- The paper does not fully specify the omitted fourth `r = 1` AQSM output.
- The paper does not fully specify a general AQSM block-selection schedule for all larger scale factors, especially `r = 3`.
- The histogram denominator printed in the paper appears inconsistent with a `2^m x 2^m` watermark; this example avoids dependence on that ambiguity because `H(127) = 0`.
- The paper gives circuit figures, but this note does not reconstruct missing gate-level details beyond the logical basis-state rules stated in the text and tables.

Conclusion:

This walkthrough is a quantum-state/register version of the same example. It is mathematically consistent with the explicit `r = 1` parts of the paper and remains directly implementable as a matrix simulation.
