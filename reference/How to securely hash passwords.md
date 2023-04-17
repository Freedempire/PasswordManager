# How to securely hash passwords

From: <https://security.stackexchange.com/questions/211/how-to-securely-hash-passwords>

> Note: This answer was written in 2013. Many things have changed in the following years, which means that this answer should primarily be seen as how best practices used to be in 2013.

## The Theory

We need to hash passwords as a second line of defence. A server which can authenticate users necessarily contains, somewhere in its entrails, some data which can be used to validate a password. A very simple system would just store the passwords themselves, and validation would be a simple comparison. But if a hostile outsider were to gain a simple glimpse at the contents of the file or database table which contains the passwords, then that attacker would learn a lot. Unfortunately, such partial, read-only breaches do occur in practice (a mislaid backup tape, a decommissioned but not wiped-out hard disk, an aftermath of a SQL injection attack -- the possibilities are numerous).

Since the overall contents of a server that can validate passwords are necessarily sufficient to indeed validate passwords, an attacker who obtained a read-only snapshot of the server is in a position to make an offline dictionary attack: he tries potential passwords until a match is found. This is unavoidable. So we want to make that kind of attack as hard as possible. Our tools are the following:

- Cryptographic hash functions: these are fascinating mathematical objects which everybody can compute efficiently, and yet nobody knows how to invert them. This looks good for our problem - the server could store a hash of a password; when presented with a putative password, the server just has to hash it to see if it gets the same value; and yet, knowing the hash does not reveal the password itself.
- Salts: among the advantages of the attacker over the defender is parallelism. The attacker usually grabs a whole list of hashed passwords, and is interested in breaking as many of them as possible. He may try to attack several in parallel. For instance, the attacker may consider one potential password, hash it, and then compare the value with 100 hashed passwords; this means that the attacker shares the cost of hashing over several attacked passwords. A similar optimisation is precomputed tables, including [rainbow tables](https://en.wikipedia.org/wiki/Rainbow_table); this is still parallelism, with a space-time change of coordinates.
  The common characteristic of all attacks which use parallelism is that they work over several passwords which were processed with the exact same hash function. Salting is about using not one hash function, but a lot of distinct hash functions; ideally, each instance of password hashing should use its own hash function. A salt is a way to select a specific hash function among a big family of hash functions. Properly applied salts will completely thwart parallel attacks (including rainbow tables).
- Slowness: computers become faster over time (Gordon Moore, co-founder of Intel, theorized it in his famous law). Human brains do not. This means that attackers can "try" more and more potential passwords as years pass, while users cannot remember more and more complex passwords (or flatly refuse to). To counter that trend, we can make hashing inherently slow by defining the hash function to use a lot of internal iterations (thousands, possibly millions).

We have a few standard cryptographic hash functions; the most famous are [MD5](https://en.wikipedia.org/wiki/MD5) and the [SHA family](https://en.wikipedia.org/wiki/Secure_Hash_Algorithm). Building a secure hash function out of elementary operations is far from easy. When cryptographers want to do that, they think hard, then harder, and organize a tournament where the functions fight each other fiercely. When hundreds of cryptographers gnawed and scraped and punched at a function for several years and found nothing bad to say about it, then they begin to admit that maybe that specific function could be considered as more or less secure. This is just what happened in the [SHA-3 competition](https://en.wikipedia.org/wiki/NIST_hash_function_competition). We have to use this way of designing hash function because we know no better way. Mathematically, we do not know if secure hash functions actually exist; we just have "candidates" (that's the difference between "it cannot be broken" and "nobody in the world knows how to break it").

A basic hash function, even if secure as a hash function, is not appropriate for password hashing, because:

- it is unsalted, allowing for parallel attacks ([rainbow tables](https://freerainbowtables.com/) for MD5 or SHA-1 can be obtained for free, you do not even need to recompute them yourself);
- it is way too fast, and gets faster with technological advances. With a recent GPU (i.e. off-the-shelf consumer product which everybody can buy), hashing rate is counted in billions of passwords per second.

So we need something better. It so happens that slapping together a hash function and a salt, and iterating it, is not easier to do than designing a hash function -- at least, if you want the result to be secure. There again, you have to rely on standard constructions which have survived the continuous onslaught of vindicative cryptographers.

## Good Password Hashing Functions

### PBKDF2

[PBKDF2](https://en.wikipedia.org/wiki/PBKDF2) comes from [PKCS#5](https://datatracker.ietf.org/doc/html/rfc2898). It is parameterized with an iteration count (an integer, at least 1, no upper limit), a salt (an arbitrary sequence of bytes, no constraint on length), a required output length (PBKDF2 can generate an output of configurable length), and an "underlying PRF". In practice, PBKDF2 is always used with [HMAC](https://en.wikipedia.org/wiki/Hash-based_message_authentication_code), which is itself a construction built over an underlying hash function. So when we say "PBKDF2 with SHA-1", we actually mean "PBKDF2 with HMAC with SHA-1".

Advantages of PBKDF2:

- Has been specified for a long time, seems unscathed for now.
- Is already implemented in various framework (e.g. it is provided with .NET).
- Highly configurable (although some implementations do not let you choose the hash function, e.g. the one in .NET is for SHA-1 only).
- Received NIST blessings (modulo the difference between hashing and key derivation; see later on).
- Configurable output length (again, see later on).

Drawbacks of PBKDF2:

- CPU-intensive only, thus amenable to high optimization with GPU (the defender is a basic server which does generic things, i.e. a PC, but the attacker can spend his budget on more specialized hardware, which will give him an edge).
- You still have to manage the parameters yourself (salt generation and storage, iteration count encoding...). There is a [standard encoding for PBKDF2 parameters](https://datatracker.ietf.org/doc/html/rfc2898#appendix-A.2) but it uses ASN.1 so most people will avoid it if they can (ASN.1 can be tricky to handle for the non-expert).

### bcrypt

[bcrypt](https://en.wikipedia.org/wiki/Bcrypt) was designed by reusing and expanding elements of a block cipher called [Blowfish](https://en.wikipedia.org/wiki/Blowfish_%28cipher%29). The iteration count is a power of two, which is a tad less configurable than PBKDF2, but sufficiently so nevertheless. This is the core password hashing mechanism in the OpenBSD operating system.

Advantages of bcrypt:

- Many available implementations in various languages (see the links at the end of the Wikipedia page).
- More resilient to GPU; this is due to details of its internal design. The bcrypt authors made it so voluntarily: they reused Blowfish because Blowfish was based on an internal RAM table which is constantly accessed and modified throughout the processing. This makes life much harder for whoever wants to speed up bcrypt with a GPU (GPU are not good at making a lot of memory accesses in parallel). See [here](https://security.stackexchange.com/questions/4781/do-any-security-experts-recommend-bcrypt-for-password-storage/6415#6415) for some discussion.
- Standard output encoding which includes the salt, the iteration count and the output as one simple to store character string of printable characters.

Drawbacks of bcrypt:

- Output size is fixed: 192 bits.
- While bcrypt is good at thwarting GPU, it can still be thoroughly optimized with [FPGA](https://en.wikipedia.org/wiki/Field-programmable_gate_array): modern FPGA chips have a lot of small embedded RAM blocks which are very convenient for running many bcrypt implementations in parallel within one chip. [It has been done.](https://openwall.info/wiki/john/FPGA)
- Input password size is limited to 51 characters. In order to handle longer passwords, one has to [combine bcrypt with a hash function](https://security.stackexchange.com/questions/6623/pre-hash-password-before-applying-bcrypt-to-avoid-restricting-password-length) (you hash the password and then use the hash value as the "password" for bcrypt). Combining cryptographic primitives is known to be dangerous (see above) so such games cannot be recommended on a general basis.

### scrypt

[scrypt](https://en.wikipedia.org/wiki/Scrypt) is a much newer construction (designed in 2009) which builds over PBKDF2 and a stream cipher called [Salsa20/8](https://en.wikipedia.org/wiki/Salsa20), but these are just tools around the core strength of scrypt, which is RAM. scrypt has been designed to inherently use a lot of RAM (it generates some pseudo-random bytes, then repeatedly reads them in a pseudo-random sequence). "Lots of RAM" is something which is hard to make parallel. A basic PC is good at RAM access, and will not try to read dozens of unrelated RAM bytes simultaneously. An attacker with a GPU or a FPGA will want to do that, and will find it difficult.

Advantages of scrypt:

- A PC, i.e. exactly what the defender will use when hashing passwords, is the most efficient platform (or close enough) for computing scrypt. The attacker no longer gets a boost by spending his dollars on GPU or FPGA.
- One more way to tune the function: memory size.

Drawbacks of scrypt:

- Still new (my own rule of thumb is to wait at least 5 years of general exposure, so no scrypt for production until 2014 - but, of course, it is best if other people try scrypt in production, because this gives extra exposure).
- Not as many available, ready-to-use implementations for various languages.
- Unclear whether the CPU / RAM mix is optimal. For each of the pseudo-random RAM accesses, scrypt still computes a hash function. A cache miss will be about 200 clock cycles, one SHA-256 invocation is close to 1000. There may be room for improvement here.
- Yet another parameter to configure: memory size.

### OpenPGP Iterated And Salted S2K

I cite this one because you will use it if you do password-based file encryption with GnuPG. That tool follows the OpenPGP format which defines its own password hashing functions, called "Simple S2K", "Salted S2K" and "Iterated and Salted S2K". Only the third one can be deemed "good" in the context of this answer. It is defined as the hash of a very long string (configurable, up to about 65 megabytes) consisting of the repetition of an 8-byte salt and the password.

As far as these things go, OpenPGP's Iterated And Salted S2K is decent; it can be considered as similar to PBKDF2, with less configurability. You will very rarely encounter it outside of OpenPGP, as a stand-alone function.

### Unix "crypt"

Recent Unix-like systems (e.g. Linux), for validating user passwords, use iterated and salted variants of the [crypt()](https://en.wikipedia.org/wiki/Crypt_%28C%29) function based on good hash functions, with thousands of iterations. This is reasonably good. Some systems can also use bcrypt, which is better.

The old crypt() function, based on the [DES block cipher](https://en.wikipedia.org/wiki/Data_Encryption_Standard), is not good enough:

- It is slow in software but fast in hardware, and can be made fast in software too but only when computing several instances in parallel (technique known as [SWAR](https://en.wikipedia.org/wiki/SWAR) or "bitslicing"). Thus, the attacker is at an advantage.
- It is still quite fast, with only 25 iterations.
- It has a 12-bit salt, which means that salt reuse will occur quite often.
- It truncates passwords to 8 characters (characters beyond the eighth are ignored) and it also drops the upper bit of each character (so you are more or less stuck with ASCII).

But the more recent variants, which are active by default, will be fine.

## Bad Password Hashing Functions

About everything else, in particular virtually every homemade method that people relentlessly invent.

For some reason, many developers insist on designing function themselves, and seem to assume that "secure cryptographic design" means "throw together every kind of cryptographic or non-cryptographic operation that can be thought of". See [this question](https://security.stackexchange.com/questions/25585/is-my-developers-home-brew-password-security-right-or-wrong-and-why) for an example. The underlying principle seems to be that the sheer complexity of the resulting utterly tangled mess of instruction will befuddle attackers. In practice, though, the developer himself will be more confused by his own creation than the attacker.

**Complexity is bad. Homemade is bad. New is bad.** If you remember that, you'll avoid 99% of problems related to password hashing, or cryptography, or even security in general.

Password hashing in Windows operating systems used to be [mindbogglingly awful](https://security.stackexchange.com/questions/2881/is-there-any-advantage-to-splitting-a-password/2883#2883) and now is just terrible (unsalted, non-iterated MD4).

## Key Derivation

Up to now, we considered the question of hashing passwords. A closely related problem is transforming a password into a symmetric key which can be used for encryption; this is called [key derivation](https://en.wikipedia.org/wiki/Key_derivation_function) and is the first thing you do when you "encrypt a file with a password".

It is possible to make contrived examples of password hashing functions which are secure for the purpose of storing a password validation token, but terrible when it comes to generating symmetric keys; and the converse is equally possible. But these examples are very "artificial". For *practical* functions like the one described above:

- The output of a password hashing function is acceptable as a symmetric key, after possible truncation to the required size.
- A Key Derivation Function can serve as a password hashing function as long as the "derived key" is long enough to avoid "generic preimages" (the attacker is just lucky and finds a password which yields the same output). An output of more than 100 bits or so will be enough.

Indeed, PBKDF2 and scrypt are KDF, not password hashing function -- and NIST "approves" of PBKDF2 as a KDF, not explicitly as a password hasher (but it is possible, with only a very minute amount of hypocrisy, to read NIST's prose in such a way that it seems to say that PBKDF2 is good for hashing passwords).

Conversely, bcrypt is really a [block cipher](https://en.wikipedia.org/wiki/Block_cipher) (the bulk of the password processing is the "key schedule") which is then used in [CTR mode](https://en.wikipedia.org/wiki/Block_cipher_modes_of_operation#Counter_.28CTR.29) to produce three blocks (i.e. 192 bits) of pseudo-random output, making it a kind of hash function. bcrypt can be turned into a KDF with a little surgery, by using the block cipher in CTR mode for more blocks. But, as usual, we cannot recommend such homemade transforms. Fortunately, 192 bits are already more than enough for most purposes (e.g. symmetric encryption with [GCM](https://en.wikipedia.org/wiki/Galois/Counter_Mode) or [EAX](https://en.wikipedia.org/wiki/EAX_mode) only needs a 128-bit key).

## Miscellaneous Topics

### How many iterations?

As much as possible! This salted-and-slow hashing is an arms race between the attacker and the defender. You use many iterations to make the hashing of a password harder for everybody. To improve security, you should set that number as high as you can tolerate on your server, given the tasks that your server must otherwise fulfill. Higher is better.

### Collisions and MD5

MD5 is *broken*: it is computationally easy to find a lot of pairs of distinct inputs which hash to the same value. These are called *collisions*.

However, **collisions are not an issue for password hashing**. Password hashing requires the hash function to be resistant to *preimages*, not to collisions. Collisions are about finding pairs of messages which give the same output without restriction, whereas in password hashing the attacker must find a message which yields a given output that the attacker does not get to choose. This is quite different. As far as we known, MD5 (digest sizes 128 bit) is still (almost) as strong as it has ever been with regards to preimages (there is a [theoretical attack](https://www.iacr.org/archive/eurocrypt2009/54790136/54790136.pdf) which is still very far in the ludicrously impossible to run in practice).

The real problem with MD5 as it is commonly used in password hashing is that it is very fast, and unsalted. However, PBKDF2 used with MD5 would be robust. You should still use SHA-1 or SHA-256 with PBKDF2, but for Public Relations. People get nervous when they hear "MD5".

### Salt Generation

The main and only point of the salt is to be as *unique* as possible. Whenever a salt value is *reused anywhere*, this has the potential to help the attacker.

For instance, if you use the user name as salt, then an attacker (or several colluding attackers) could find it worthwhile to build rainbow tables which attack the password hashing function when the salt is "admin" (or "root" or "joe") because there will be several, possibly many sites around the world which will have a user named "admin". Similarly, when a user changes his password, he usually keeps his name, leading to salt reuse. Old passwords are valuable targets, because users have the habit of reusing passwords in several places (that's known to be a bad idea, and advertised as such, but they will do it nonetheless because it makes their life easier), and also because people tend to generate their passwords "in sequence": if you learn that Bob's old password is "SuperSecretPassword37", then Bob's current password is probably "SuperSecretPassword38" or "SuperSecretPassword39".

The cheap way to obtain uniqueness is to use *randomness*. If you generate your salt as a sequence of random bytes from the [cryptographically secure PRNG](https://en.wikipedia.org/wiki/Cryptographically_secure_pseudorandom_number_generator) that your operating system offers (`/dev/urandom`, `CryptGenRandom()`...) then you will get salt values which will be "unique with a sufficiently high probability". *16 bytes are enough* so that you will never see a salt collision in your life, which is overkill but simple enough.

[UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier) are a standard way of generating "unique" values. Note that "version 4" UUID just use randomness (122 random bits), like explained above. A lot of programming frameworks offer simple to use functions to generate UUID on demand, and they can be used as salts.

### Salt Secrecy

Salts are *not* meant to be secret; otherwise we would call them keys. You do not need to make salts public, but if you have to make them public (e.g. to support client-side hashing), then don't worry too much about it. Salts are there for *uniqueness*. Strictly speaking, the salt is nothing more than the selection of a specific hash function within a big family of functions.

### "Pepper"

Cryptographers can never let a metaphor alone; they must extend it with further analogies and bad puns. "Peppering" is about using a secret salt, i.e. a key. If you use a "pepper" in your password hashing function, then you are switching to a quite different kind of cryptographic algorithm; namely, you are computing a [Message Authentication Code](https://en.wikipedia.org/wiki/Message_authentication_code) over the password. The MAC key is your "pepper".

Peppering makes sense if you can have a secret key which the attacker will not be able to read. *Remember that we use password hashing because we consider that an attacker could grab a copy of the server database, or possible of the whole disk of the server.* A typical scenario would be a server with two disks in [RAID 1](https://en.wikipedia.org/wiki/RAID#RAID_1). One disk fails (electronic board fries - this happens a lot). The sysadmin replaces the disk, the mirror is rebuilt, no data is lost due to the magic of RAID 1. Since the old disk is dysfunctional, the sysadmin cannot easily wipe its contents. He just discards the disk. The attacker searches through the garbage bags, retrieves the disk, replaces the board, and lo! he has a complete image of the whole server system, including database, configuration files, binaries, operating system... the full monty, as the British say. For peppering to be really applicable, you need to be in a special setup where there is something more than a PC with disks; you need an [HSM (hardware security module)](https://en.wikipedia.org/wiki/Hardware_security_module). HSM are very expensive, both in hardware and in operational procedure. But with an HSM, you can just use a secret "pepper" and process passwords with a simple [HMAC (hash-based message authentication code)](https://en.wikipedia.org/wiki/HMAC) (e.g. with SHA-1 or SHA-256). This will be vastly more efficient than bcrypt/PBKDF2/scrypt and their cumbersome iterations. Also, usage of an HSM will look extremely professional when doing a WebTrust audit.

### Client-side hashing

Since hashing is (deliberately) expensive, it could make sense, in a client-server situation, to harness the CPU of the connecting clients. After all, when 100 clients connect to a single server, the clients collectively have a lot more muscle than the server.

To perform client-side hashing, the communication protocol must be enhanced to support sending the salt back to the client. This implies an extra round-trip, when compared to the simple client-sends-password-to-server protocol. This may or may not be easy to add to your specific case.

Client-side hashing is difficult in a Web context because the client uses JavaScript, which is quite anemic for CPU-intensive tasks.

In the context of [SRP](https://en.wikipedia.org/wiki/Secure_Remote_Password_protocol), password hashing necessarily occurs on the client side.

## Conclusion

Use bcrypt. PBKDF2 is not bad either. If you use scrypt you will be a "slightly early adopter" with the risks that are implied by this expression; but it would be a good move for scientific progress ("crash dummy" is a very honourable profession).
