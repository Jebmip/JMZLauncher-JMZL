# Security Features

## Implemented Security Measures

### ✓ SHA1 Hash Verification (Added: Feb 17, 2026)

All downloaded files are verified using SHA1 hashes provided by Mojang:

**What's verified:**
- Client JAR files (main game executable)
- All library files (dependencies)
- Asset index files
- All game assets (textures, sounds, etc.)

**How it works:**
1. Download file to temporary location
2. Calculate SHA1 hash of downloaded file
3. Compare with expected hash from Mojang's manifest
4. If match: Move to final location
5. If mismatch: Delete file and report error

**Benefits:**
- Detects corrupted downloads
- Prevents tampered files
- Ensures file integrity
- Protects against MITM attacks (partial)

### ✓ Input Validation & Sanitization (Added: Feb 17, 2026)

All user inputs and file paths are validated to prevent injection attacks:

**Username Validation:**
- Must be 3-16 characters
- Only alphanumeric and underscores
- Prevents command injection
- Follows Minecraft username rules

**Version Name Validation:**
- Alphanumeric, dots, hyphens, underscores only
- Prevents directory traversal attacks
- No `..`, `/`, or `\` allowed

**Main Class Validation:**
- Only allows known Minecraft main classes
- Prevents arbitrary code execution
- Whitelist approach

**Classpath Validation:**
- All JARs must be in our directories
- Prevents loading external malicious code
- Path traversal protection

**Benefits:**
- Prevents command injection
- Stops directory traversal attacks
- Blocks arbitrary code execution
- Validates all external inputs

**Implementation:**
- Uses Python's `hashlib.sha1()` for verification
- Automatic re-download if hash fails
- Skips re-downloading if file exists and hash matches
- Shows verification status in console

## Current Security Status

### ✓ Secure Features
- Official Mojang servers only
- SHA1 hash verification for all downloads
- Username validation (3-16 chars, alphanumeric + underscore)
- Version name validation (prevents directory traversal)
- Main class whitelist (prevents arbitrary code execution)
- Classpath path validation (only trusted directories)
- No credential storage (offline mode)
- Local file operations only
- Standard Python libraries
- Temporary file downloads (atomic operations)

### ⚠️ Known Limitations
- No sandbox for Java process (inherent to Minecraft)
- No rate limiting on downloads
- No file size limits before download

### 🔒 Planned Security Improvements
1. File size checks before downloading
2. Better error handling
3. Download rate limiting
4. Logging of security events

## Security Best Practices

**For Users:**
- Only download from the official launcher
- Keep Java updated
- Don't modify downloaded files manually
- Use strong passwords when Microsoft auth is added

**For Developers:**
- Always verify hashes before using files
- Keep dependencies updated
- Review code changes carefully
- Test with various Minecraft versions

## Reporting Security Issues

If you find a security vulnerability:
1. Do NOT open a public issue
2. Contact the developer privately
3. Provide detailed reproduction steps
4. Allow time for a fix before disclosure

## Version History

- **v1.2** (Feb 17, 2026): Added input validation & sanitization
- **v1.1** (Feb 17, 2026): Added SHA1 hash verification
- **v1.0** (Feb 17, 2026): Initial release with basic security
