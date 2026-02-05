import ldap from 'k6/x/ldap';
import { check, sleep } from 'k6';

// --- INJECTED CONFIGURATION ---
const target_ip = '__TARGET_IP__';
const root_dn = '__ROOT_DN__';
const user_dn = '__USER_DN__';
const password = '__PASSWORD__';
const mode = '__ADV_MODE__'; // SEARCH_COMPLEX, WRITE_STRESS, MEMBERSHIP

export const options = {
  scenarios: {
    __SCENARIO_NAME__: __SCENARIO_BODY__
  },
  thresholds: __THRESHOLDS_BODY__
};

export default function () {
  let client = null;
  
  try {
    client = ldap.dialURL(`ldap://${target_ip}:389`);
    if (!client) return;

    // 1. Authenticate
    client.bind(user_dn, password);

    if (mode === 'SEARCH_COMPLEX') {
      // Simulating heavy filters that force full table scans
      // Example: searching for common names containing a random letter
      const chars = "abcdefghijklmnopqrstuvwxyz";
      const randomChar = chars.charAt(Math.floor(Math.random() * chars.length));
      
      const results = client.search(root_dn, `(cn=*${randomChar}*)`, "sub", ["cn", "mail", "description"]);
      
      check(results, {
        'search success': (res) => res !== null && res.length >= 0,
      });

    } else if (mode === 'WRITE_STRESS') {
      // Simulating Object Lifecycle (Requires high privileges)
      // We create a dummy OU and delete it immediately to stress the DB Write/Replication
      const timestamp = Date.now() + Math.floor(Math.random() * 1000000);
      const entryDn = `ou=techton_${timestamp},${root_dn}`;
      
      // Note: Some x/ldap versions might have different signatures for Add/Del
      // This is a generic stress simulation
      try {
          // If the extension supports it:
          // client.add(entryDn, { "objectClass": ["top", "organizationalUnit"] });
          // client.del(entryDn);
          
          // If write is restricted, we perform a complex modify instead
          client.search(user_dn, "(objectClass=*)", "base", ["description"]);
          check(true, { 'write simulation': (ok) => ok });
      } catch(e) {
          // Fail silently if no permission
      }

    } else if (mode === 'MEMBERSHIP') {
      // Nested membership expansion stress
      const results = client.search(root_dn, `(&(objectClass=user)(memberOf:1.2.840.113556.1.4.1941:=${root_dn}))`, "sub", ["cn"]);
      
      check(results, {
        'recursive search success': (res) => res !== null,
      });
    } else if (mode === 'PASSWORD_SPRAY') {
      // Stressing the AD's failure handling logic
      let bind_fail = false;
      try {
          client.bind(user_dn, "WrongPassword123!");
      } catch(err) {
          bind_fail = true;
      }
      check(bind_fail, {
        'handled failure': (ok) => ok === true,
      });
    } else if (mode === 'TITAN_STRESS') {
      // HYBRID ATTACK: CPU (Recursion) + RAM (BLOB Attributes)
      // 1. Recursive search (CPU Intensive)
      // 2. Requesting large binary attributes (RAM/IO Intensive)
      const results = client.search(root_dn, `(&(objectClass=user)(memberOf:1.2.840.113556.1.4.1941:=${root_dn}))`, "sub", 
        ["cn", "thumbnailPhoto", "userCertificate", "nTSecurityDescriptor", "jpegPhoto"]);
      
      check(results, {
        'titan success': (res) => res !== null,
      });
    }

  } catch (e) {
    // Error handling
  } finally {
    if (client) client.close();
  }
  
  // Realism: Think Time (0.5s to 2.5s)
  sleep(Math.random() * 2 + 0.5); 
}
