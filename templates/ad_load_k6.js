import ldap from 'k6/x/ldap';
import { check, sleep } from 'k6';

// --- CONFIGURATION (Injected by Techton) ---
const target_ip = '__TARGET_IP__';
const user_dn_template = '__USER_DN__'; // e.g. CN=user1,OU=...
const password = '__PASSWORD__';

export const options = {
  scenarios: {
    login_storm: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '__RAMPUP__s', target: __THREADS__ }, // Ramp up to N users
        { duration: '__DURATION__s', target: __THREADS__ }, // Stay there
        { duration: '10s', target: 0 },         // Ramp down
      ],
      gracefulStop: '0s',
    },
  },
  thresholds: {
    'ldap_response_time': ['p(95)<2000'], // Fail if 95% of requests take > 2s
    'ldap_result_code': ['rate<0.01'],    // Fail if error rate > 1%
  },
};

const client = new ldap.Client({
  url: `ldap://${target_ip}:389`,
});

export default function () {
  // 1. Connect
  try {
    client.connect();
    
    // 2. Bind (Login)
    // In k6, we simulate distinct users if needed, or stress one account
    // For raw stress test, stressing one account is often enough to kill CPU
    const bind_success = client.bind(user_dn_template, password);

    check(bind_success, {
      'bind success': (ok) => ok === true,
    });

    // 3. Unbind (Logout) - Important to close socket
    client.unbind();
    
    // Sleep random to behave like human (0.5s - 1.5s)
    sleep(Math.random() * 1 + 0.5);

  } catch (e) {
    console.error('LDAP Error:', e.message);
  }
}
