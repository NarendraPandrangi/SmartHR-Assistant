// === FIREBASE CONFIGURATION ===
// Replace with your actual Firebase project config credentials
const firebaseConfig = {
  apiKey: "AIzaSyBD-tks12FGzcrl4yt-PaHn-HKRcNS3v7U",
  authDomain: "smarthr-assistant.firebaseapp.com",
  projectId: "smarthr-assistant",
  storageBucket: "smarthr-assistant.firebasestorage.app",
  messagingSenderId: "99314326580",
  appId: "1:99314326580:web:b762f6e8750cf2ef0afe61",
  measurementId: "G-NKPBMD3FEE"
};

// Initialize Firebase
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}

const auth = firebase.auth();
const googleProvider = new firebase.auth.GoogleAuthProvider();

// App Settings
// The backend URL is injected from the Vercel/Render .env automatically during build.
const injectedUrl = "{BACKEND_URL_INJECT}";
const BACKEND_DOMAIN = injectedUrl.startsWith("{") ? "http://localhost:8000" : injectedUrl;

const FASTAPI_URL = `${BACKEND_DOMAIN}/api/chat`;
const UPLOAD_URL = `${BACKEND_DOMAIN}/api/upload`;

// Page State Management
const isAuthPage = document.getElementById('auth-container') !== null;
const isChatPage = document.getElementById('chat-container') !== null;

// Ensure authentication checks
auth.onAuthStateChanged(user => {
  if (user) {
    console.log("Logged in as:", user.email);
    if (isAuthPage || document.getElementById('landing-container')) {
      // Redirect to Chat 
      window.location.href = "chat.html";
    }
  } else {
    console.log("Not logged in.");
    if (isChatPage) {
      // Redirect to Auth
      window.location.href = "auth.html";
    }
  }
});


// === AUTHENTICATION LOGIC (auth.html) ===
if (isAuthPage) {
  // Elements
  const loginView = document.getElementById('login-view');
  const signupView = document.getElementById('signup-view');
  const linkSignup = document.getElementById('link-signup');
  const linkLogin = document.getElementById('link-login');

  // Check URL Hash for Signup Auto-load
  if (window.location.hash === '#signup') {
    loginView.classList.add('hidden');
    signupView.classList.remove('hidden');
  }

  // Toggling Views
  linkSignup.addEventListener('click', (e) => {
    e.preventDefault();
    loginView.classList.add('hidden');
    signupView.classList.remove('hidden');
  });

  linkLogin.addEventListener('click', (e) => {
    e.preventDefault();
    signupView.classList.add('hidden');
    loginView.classList.remove('hidden');
  });

  // Log In w/ Email
  document.getElementById('btn-login').addEventListener('click', () => {
    const email = document.getElementById('login-email').value;
    const pass = document.getElementById('login-password').value;
    if(!email || !pass) return alert("Please fill all fields");

    auth.signInWithEmailAndPassword(email, pass)
      .catch(error => alert(`Login Error: ${error.message}`));
  });

  // Sign Up w/ Email
  document.getElementById('btn-signup').addEventListener('click', () => {
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const pass = document.getElementById('signup-password').value;
    const confirm = document.getElementById('signup-confirm').value;

    if(!name || !email || !pass || !confirm) return alert("All fields are required");
    if(pass !== confirm) return alert("Passwords do not match!");

    auth.createUserWithEmailAndPassword(email, pass)
      .then(userCredential => {
        // Optional: Update profile name
        return userCredential.user.updateProfile({ displayName: name });
      })
      .catch(error => alert(`Signup Error: ${error.message}`));
  });

  // Google Sign In (Login & Signup use same method)
  const googleSignIn = () => {
    auth.signInWithPopup(googleProvider)
      .catch(error => alert(`Google Sign-In Error: ${error.message}`));
  };

  document.getElementById('btn-google-login').addEventListener('click', googleSignIn);
  document.getElementById('btn-google-signup').addEventListener('click', googleSignIn);
}

// === CHAT LOGIC (chat.html) ===
if (isChatPage) {
  const btnLogout = document.getElementById('btn-logout');
  const btnSend = document.getElementById('btn-send');
  const chatInput = document.getElementById('chat-input');
  const chatBox = document.getElementById('chat-box');

  btnLogout.addEventListener('click', () => {
    auth.signOut();
  });

  const appendMessage = (text, sender) => {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.textContent = text;
    chatBox.appendChild(msgDiv);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll
  };

  const setTypingIndicator = (show) => {
    if (show) {
      const msgDiv = document.createElement('div');
      msgDiv.classList.add('message', 'bot', 'typing-indicator');
      msgDiv.id = 'typing';
      msgDiv.innerHTML = "Thinking...";
      chatBox.appendChild(msgDiv);
      chatBox.scrollTop = chatBox.scrollHeight;
    } else {
      const typing = document.getElementById('typing');
      if (typing) typing.remove();
    }
  };

  const handleSend = async () => {
    const query = chatInput.value.trim();
    if (!query) return;

    // UI Updates
    appendMessage(query, 'user');
    chatInput.value = '';
    setTypingIndicator(true);

    try {
      const res = await fetch(FASTAPI_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query })
      });

      if (!res.ok) throw new Error("Backend server error");

      const data = await res.json();
      setTypingIndicator(false);
      appendMessage(data.answer, 'bot');
      
      // Optional: Log context_used for debugging
      console.log("Context Used:", data.context_used);

    } catch (err) {
      setTypingIndicator(false);
      appendMessage(`Error: ${err.message}. Make sure the FastAPI server is running on localhost:8000.`, 'bot');
    }
  };

  btnSend.addEventListener('click', handleSend);
  chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleSend();
  });

  // Handle File Upload
  const fileUpload = document.getElementById('file-upload');
  if (fileUpload) {
    fileUpload.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      
      appendMessage(`Uploading file: ${file.name}...`, 'user');
      setTypingIndicator(true);
      
      const formData = new FormData();
      formData.append("file", file);
      
      try {
        const res = await fetch(UPLOAD_URL, {
          method: "POST",
          body: formData
        });
        
        if (!res.ok) throw new Error("Upload failed on the server.");
        
        const data = await res.json();
        setTypingIndicator(false);
        appendMessage(`Success! ${file.name} has been downloaded and indexed into my knowledge base.`, 'bot');
      } catch (err) {
        setTypingIndicator(false);
        appendMessage(`Error uploading file: ${err.message}`, 'bot');
      }
      
      // Reset input
      fileUpload.value = "";
    });
  }
}
