#!/usr/bin/env python3
"""
Test if Java can make HTTPS requests to Ely.by
This helps diagnose network/firewall issues
"""

import subprocess
import tempfile
from pathlib import Path

# Create a simple Java program to test HTTPS connectivity
java_code = '''
import java.net.URL;
import java.net.HttpURLConnection;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class TestElybyConnection {
    public static void main(String[] args) {
        String urlString = "https://authserver.ely.by/api/authlib-injector";
        
        System.out.println("Testing Java HTTPS connection to Ely.by...");
        System.out.println("URL: " + urlString);
        System.out.println();
        
        try {
            URL url = new URL(urlString);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("User-Agent", "authlib-injector");
            conn.setConnectTimeout(10000);
            conn.setReadTimeout(10000);
            
            int responseCode = conn.getResponseCode();
            System.out.println("Response Code: " + responseCode);
            System.out.println("Content-Type: " + conn.getContentType());
            System.out.println("Content-Length: " + conn.getContentLength());
            System.out.println();
            
            if (responseCode == 200) {
                BufferedReader in = new BufferedReader(
                    new InputStreamReader(conn.getInputStream())
                );
                StringBuilder response = new StringBuilder();
                String line;
                
                while ((line = in.readLine()) != null) {
                    response.append(line);
                }
                in.close();
                
                String content = response.toString();
                System.out.println("Response length: " + content.length() + " characters");
                System.out.println();
                System.out.println("First 200 characters:");
                System.out.println(content.substring(0, Math.min(200, content.length())));
                System.out.println();
                
                // Try to validate it's JSON
                if (content.startsWith("{") && content.contains("meta")) {
                    System.out.println("✓ SUCCESS: Valid JSON response received!");
                    System.out.println("✓ Java can successfully connect to Ely.by API");
                    System.out.println();
                    System.out.println("This means the network is working.");
                    System.out.println("If skins still don't work, the issue is likely:");
                    System.out.println("  1. Authlib-injector version incompatibility");
                    System.out.println("  2. Minecraft version compatibility");
                    System.out.println("  3. JVM argument formatting");
                } else {
                    System.out.println("✗ ERROR: Response doesn't look like valid JSON");
                    System.out.println("This might be a server-side issue");
                }
            } else {
                System.out.println("✗ ERROR: HTTP " + responseCode);
                System.out.println("The server returned an error response");
            }
            
        } catch (java.net.UnknownHostException e) {
            System.out.println("✗ ERROR: Cannot resolve hostname");
            System.out.println("Check your internet connection or DNS settings");
            System.out.println("Error: " + e.getMessage());
        } catch (java.net.ConnectException e) {
            System.out.println("✗ ERROR: Connection refused or timeout");
            System.out.println("Possible causes:");
            System.out.println("  1. Firewall blocking Java");
            System.out.println("  2. No internet connection");
            System.out.println("  3. Ely.by service is down");
            System.out.println("Error: " + e.getMessage());
        } catch (javax.net.ssl.SSLException e) {
            System.out.println("✗ ERROR: SSL/TLS error");
            System.out.println("Your Java version might be too old");
            System.out.println("Try updating to Java 17 or newer");
            System.out.println("Error: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("✗ ERROR: " + e.getClass().getName());
            System.out.println("Message: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
'''

print("Java Network Connectivity Test")
print("=" * 70)
print()
print("This test checks if Java can make HTTPS requests to Ely.by")
print("This helps diagnose firewall, SSL, or network issues")
print()

# Check if Java is available
try:
    result = subprocess.run(
        ['java', '-version'],
        capture_output=True,
        text=True,
        timeout=5
    )
    java_version = result.stderr.split('\n')[0]
    print(f"Java found: {java_version}")
    print()
except Exception as e:
    print(f"✗ Error: Java not found or not in PATH")
    print(f"  {e}")
    print()
    print("Please install Java and try again")
    exit(1)

# Create temporary directory for Java file
with tempfile.TemporaryDirectory() as tmpdir:
    tmppath = Path(tmpdir)
    java_file = tmppath / "TestElybyConnection.java"
    
    # Write Java code
    with open(java_file, 'w') as f:
        f.write(java_code)
    
    print("Compiling test program...")
    try:
        result = subprocess.run(
            ['javac', str(java_file)],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=tmppath
        )
        
        if result.returncode != 0:
            print(f"✗ Compilation failed:")
            print(result.stderr)
            exit(1)
        
        print("✓ Compiled successfully")
        print()
        
    except Exception as e:
        print(f"✗ Error compiling: {e}")
        exit(1)
    
    # Run the test
    print("Running network test...")
    print("-" * 70)
    try:
        result = subprocess.run(
            ['java', 'TestElybyConnection'],
            capture_output=False,
            text=True,
            timeout=30,
            cwd=tmppath
        )
    except subprocess.TimeoutExpired:
        print()
        print("✗ Test timed out after 30 seconds")
        print("This suggests a network connectivity issue")
    except Exception as e:
        print(f"✗ Error running test: {e}")

print()
print("-" * 70)
print()
print("Test complete!")
print()
print("If the test succeeded, authlib-injector should work.")
print("If it failed, you need to fix the network/firewall issue first.")
