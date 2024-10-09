async function register() {
  // Fetch options from the server
  const options = await getMakeCredentialsOptions();

  options.user.id = Uint8Array.from(window.atob(options.user.id), (c) =>
    c.charCodeAt(0)
  );
  options.challenge = Uint8Array.from(window.atob(options.challenge), (c) =>
    c.charCodeAt(0)
  );

  if (options.excludeCredentials) {
    for (let cred of options.excludeCredentials) {
      cred.id = Uint8Array.from(window.atob(cred.id), (c) => c.charCodeAt(0));
    }
  }

  // Create a new credential
  navigator.credentials
    .create({ publicKey: options })
    .then((credential) => {
      // Send the new credential to the server
      sendAttestationToServer(credential);
    })
    .catch((err) => {
      console.error(err);
    });
}

async function login() {
  // Fetch options from the server
  const options = await getGetAssertionOptions();

  // Convert base64 strings to ArrayBuffers
  options.challenge = Uint8Array.from(window.atob(options.challenge), (c) =>
    c.charCodeAt(0)
  );

  if (options.allowCredentials) {
    for (let cred of options.allowCredentials) {
      cred.id = Uint8Array.from(window.atob(cred.id), (c) => c.charCodeAt(0));
    }
  }

  // Get an assertion
  navigator.credentials
    .get({ publicKey: options })
    .then((assertion) => {
      // Send the assertion to the server
      sendAssertionToServer(assertion);
    })
    .catch((err) => {
      console.error(err);
    });
}

async function getMakeCredentialsOptions() {
  // In a real application, fetch these options from the server
  return {
    rp: {
      name: "BIL",
      id: window.location.hostname,
    },
    user: {
      id: window.btoa("unique-user-id"), // how to generate this?
      name: "user@example.com", // ask user for this
      displayName: "user@example.com", //ask user for this
    },
    pubKeyCredParams: [
      { type: "public-key", alg: -7 },
      { type: "public-key", alg: -257 },
    ],
    authenticatorSelection: {
      authenticatorAttachment: "platform",
      requireResidentKey: false,
      userVerification: "preferred",
    },
    attestation: "direct",
    timeout: 60000,
    challenge: window.btoa("random-challenge-string"), // how to generate this?
  };
}

async function getGetAssertionOptions() {
  // In a real application, fetch these options from your server
  return {
    challenge: window.btoa("random-challenge-string"),
    allowCredentials: [
      {
        type: "public-key",
        id: window.btoa("existing-credential-id"),
        transports: ["internal"],
      },
    ],
    userVerification: "preferred",
    timeout: 60000,
  };
}

function sendAttestationToServer(credential) {
  // Send the credential to the server for verification and registration
  console.log("Credential created:", credential);
  // Implement server communication here
}

function sendAssertionToServer(assertion) {
  console.log("Assertion received:", assertion);
}

const isBiometricAvailable =
  await window?.PublicKeyCredential?.isUserVerifyingPlatformAuthenticatorAvailable();
if (!isBiometricAvailable) {
  console.log("Biometrics not available!!");
  return;
}
