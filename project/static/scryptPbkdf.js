/* 
https://github.com/juanelas/scrypt-pbkdf

MIT License

Copyright (c) 2018 Juan Hernández Serrano

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

var scryptPbkdf = function(e) {
    "use strict";
    const r = function(e) {
            function r(e, r) {
                return e << r | e >>> 32 - r
            }
            const t = e.slice(0);
            for (let e = 8; e > 0; e -= 2) t[4] ^= r(t[0] + t[12], 7), t[8] ^= r(t[4] + t[0], 9), t[12] ^= r(t[8] + t[4], 13), t[0] ^= r(t[12] + t[8], 18), t[9] ^= r(t[5] + t[1], 7), t[13] ^= r(t[9] + t[5], 9), t[1] ^= r(t[13] + t[9], 13), t[5] ^= r(t[1] + t[13], 18), t[14] ^= r(t[10] + t[6], 7), t[2] ^= r(t[14] + t[10], 9), t[6] ^= r(t[2] + t[14], 13), t[10] ^= r(t[6] + t[2], 18), t[3] ^= r(t[15] + t[11], 7), t[7] ^= r(t[3] + t[15], 9), t[11] ^= r(t[7] + t[3], 13), t[15] ^= r(t[11] + t[7], 18), t[1] ^= r(t[0] + t[3], 7), t[2] ^= r(t[1] + t[0], 9), t[3] ^= r(t[2] + t[1], 13), t[0] ^= r(t[3] + t[2], 18), t[6] ^= r(t[5] + t[4], 7), t[7] ^= r(t[6] + t[5], 9), t[4] ^= r(t[7] + t[6], 13), t[5] ^= r(t[4] + t[7], 18), t[11] ^= r(t[10] + t[9], 7), t[8] ^= r(t[11] + t[10], 9), t[9] ^= r(t[8] + t[11], 13), t[10] ^= r(t[9] + t[8], 18), t[12] ^= r(t[15] + t[14], 7), t[13] ^= r(t[12] + t[15], 9), t[14] ^= r(t[13] + t[12], 13), t[15] ^= r(t[14] + t[13], 18);
            for (let r = 0; r < 16; r++) e[r] = t[r] + e[r]
        },
        t = function(e, r) {
            for (let t = 0; t < e.length; t++) e[t] ^= r[t]
        },
        n = function(e) {
            const n = e.byteLength / 128,
                i = 16 * (2 * n - 1),
                o = e.slice(i, i + 16),
                a = new Uint32Array(e.length / 2);
            let s = !0;
            for (let i = 0; i < 2 * n; i++) {
                const n = 16 * i,
                    f = e.subarray(n, n + 16);
                t(o, f), r(o);
                const c = 16 * (i >> 1);
                if (s)
                    for (let r = 0; r < 16; r++) e[c + r] = o[r];
                else
                    for (let e = 0; e < 16; e++) a[c + e] = o[e];
                s = !s
            }
            const f = 16 * n;
            for (let r = 0; r < f; r++) e[f + r] = a[r]
        },
        i = function(e, r) {
            const i = e.byteLength / 128,
                o = new Array(r);
            for (let t = 0; t < r; t++) o[t] = e.slice(0), n(e);

            function a(e) {
                const t = 64 * (2 * i - 1);
                return new DataView(e.buffer, t, 64).getUint32(0, !0) % r
            }
            for (let i = 0; i < r; i++) {
                const r = a(e);
                t(e, o[r]), n(e)
            }
        },
        o = {
            "SHA-1": {
                outputLength: 20,
                blockSize: 64
            },
            "SHA-256": {
                outputLength: 32,
                blockSize: 64
            },
            "SHA-384": {
                outputLength: 48,
                blockSize: 128
            },
            "SHA-512": {
                outputLength: 64,
                blockSize: 128
            }
        };

    function a(e, r, t, n, i = "SHA-256") {
        return new Promise(((a, c) => {
            i in o || c(new RangeError(`Valid hash algorithm values are any of ${Object.keys(o).toString()}`)), "string" == typeof e ? e = (new TextEncoder).encode(e) : e instanceof ArrayBuffer ? e = new Uint8Array(e) : ArrayBuffer.isView(e) || c(RangeError("P should be string, ArrayBuffer, TypedArray, DataView")), "string" == typeof r ? r = (new TextEncoder).encode(r) : r instanceof ArrayBuffer ? r = new Uint8Array(r) : ArrayBuffer.isView(r) ? r = new Uint8Array(r.buffer, r.byteOffset, r.byteLength) : c(RangeError("S should be string, ArrayBuffer, TypedArray, DataView")), crypto.subtle.importKey("raw", e, "PBKDF2", !1, ["deriveBits"]).then((u => {
                const y = {
                    name: "PBKDF2",
                    hash: i,
                    salt: r,
                    iterations: t
                };
                crypto.subtle.deriveBits(y, u, 8 * n).then((e => a(e)), (u => {
                    (async function(e, r, t, n, i) {
                        if (!(i in o)) throw new RangeError(`Valid hash algorithm values are any of ${Object.keys(o).toString()}`);
                        if (!Number.isInteger(t) || t <= 0) throw new RangeError("c must be a positive integer");
                        const a = o[i].outputLength;
                        if (!Number.isInteger(n) || n <= 0 || n >= (2 ** 32 - 1) * a) throw new RangeError("dkLen must be a positive integer < (2 ** 32 - 1) * hLen");
                        const c = Math.ceil(n / a),
                            u = n - (c - 1) * a,
                            y = new Array(c);
                        0 === e.byteLength && (e = new Uint8Array(o[i].blockSize));
                        const l = await crypto.subtle.importKey("raw", e, {
                                name: "HMAC",
                                hash: {
                                    name: i
                                }
                            }, !0, ["sign"]),
                            w = async function(e, r) {
                                const t = await crypto.subtle.sign("HMAC", e, r);
                                return new Uint8Array(t)
                            };
                        for (let e = 0; e < c; e++) y[e] = await g(l, r, t, e + 1);
                        async function g(e, r, t, n) {
                            const i = await w(e, s(r, function(e) {
                                const r = new ArrayBuffer(4);
                                return new DataView(r).setUint32(0, e, !1), new Uint8Array(r)
                            }(n)));
                            let o = i;
                            for (let r = 1; r < t; r++) o = await w(e, o), f(i, o);
                            return i
                        }
                        return y[c - 1] = y[c - 1].slice(0, u), s(...y).buffer
                    })(e, r, t, n, i).then((e => a(e)), (e => c(e)))
                }))
            }), (e => c(e)))
        }))
    }

    function s(...e) {
        const r = e.reduce(((e, r) => e + r.length), 0);
        if (0 === e.length) throw new RangeError("Cannot concat no arrays");
        const t = new Uint8Array(r);
        let n = 0;
        for (const r of e) t.set(r, n), n += r.length;
        return t
    }

    function f(e, r) {
        for (let t = 0; t < e.length; t++) e[t] ^= r[t]
    }
    return e.salsa208Core = r, e.salt = function(e = 16) {
        if (!Number.isInteger(e) || e < 0) throw new RangeError("length must be integer >= 0");
        return 0 === e ? new ArrayBuffer(0) : crypto.getRandomValues(new Uint8Array(e)).buffer
    }, e.scrypt = async function(e, r, t, n) {
        if ("string" == typeof e) e = (new TextEncoder).encode(e);
        else if (e instanceof ArrayBuffer) e = new Uint8Array(e);
        else if (!ArrayBuffer.isView(e)) throw RangeError("P should be string, ArrayBuffer, TypedArray, DataView");
        if ("string" == typeof r) r = (new TextEncoder).encode(r);
        else if (r instanceof ArrayBuffer) r = new Uint8Array(r);
        else if (!ArrayBuffer.isView(r)) throw RangeError("S should be string, ArrayBuffer, TypedArray, DataView");
        if (!Number.isInteger(t) || t <= 0 || t > 137438953440) throw RangeError("dkLen is the intended output length in octets of the derived key; a positive integer less than or equal to (2^32 - 1) * hLen where hLen is 32");
        const o = void 0 !== n && void 0 !== n.N ? n.N : 131072,
            s = void 0 !== n && void 0 !== n.r ? n.r : 8,
            f = void 0 !== n && void 0 !== n.p ? n.p : 1;
        if (!Number.isInteger(o) || o <= 0 || 0 != (o & o - 1)) throw RangeError("N must be a power of 2");
        if (!Number.isInteger(s) || s <= 0 || !Number.isInteger(f) || f <= 0 || f * s > 1073741823.75) throw RangeError("Parallelization parameter p and blocksize parameter r must be positive integers satisfying p ≤ (2^32− 1) * hLen / MFLen where hLen is 32 and MFlen is 128 * r.");
        const c = await a(e, r, 1, 128 * f * s),
            u = new Uint32Array(c);
        for (let e = 0; e < f; e++) {
            const r = 32 * s,
                t = e * r,
                n = u.slice(t, t + r);
            i(n, o);
            for (let e = 0; e < 32 * s; e++) u[t + e] = n[e]
        }
        return await a(e, u, 1, t)
    }, e.scryptBlockMix = n, e.scryptROMix = i, e
}({});
