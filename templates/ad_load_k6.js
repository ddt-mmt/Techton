import ldap from 'k6/x/ldap';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// --- CONFIGURATION ---
const target_ip = '__TARGET_IP__';
const use_csv = __USE_CSV__; // Boolean flag injected by Techton
const single_user_dn = '__USER_DN__';
const single_password = '__PASSWORD__';

// Load CSV if enabled
const user_data = new SharedArray('users', function () {
  if (use_csv) {
    return open('./users.csv').split('\n').slice(1); // Skip header
  }
  return [];
});

export const options = {
  scenarios: {
    __SCENARIO_NAME__: __SCENARIO_BODY__
  },
  thresholds: __THRESHOLDS_BODY__
};

export default function () {
  if (__ITER == 0) sleep(Math.random() * 2); 

  // Determine Credentials
  let dn, pass;
  
  if (use_csv && user_data.length > 0) {
      // Pick random user from list
      const row = user_data[Math.floor(Math.random() * user_data.length)];
      if (!row) return; // Skip empty lines
      const cols = row.split(',');
      dn = cols[0].trim();
      pass = cols[1] ? cols[1].trim() : single_password; // Use CSV pass or default
  } else {
      dn = single_user_dn;
      pass = single_password;
  }

  let client = null;
  
  try {
    // 1. Dial
    try {
        client = ldap.dialURL(`ldap://${target_ip}:389`);
    } catch (e) {
        sleep(1);
        return;
    }

    if (!client) throw new Error("Client null");

    // 2. Bind
    let bind_success = false;
    try {
        client.bind(dn, pass);
        bind_success = true;
    } catch(err) {
         // Expected for wrong password/stress
    }

    check(bind_success, {
      'bind success': (ok) => ok === true,
    });

  } catch (e) {
    // Suppress
  } finally {
    if (client) {
        try { client.close(); } catch(e) {}
    }
  }
  
  sleep(Math.random() * 0.5 + 0.1); 
}