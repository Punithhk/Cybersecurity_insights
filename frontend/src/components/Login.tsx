import React, { useState } from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';


// 1. Strongly type the user profile from our FastAPI backend
interface UserProfile {
  email: string;
  name: string;
  picture: string;
  id: string;
}

// 2. Define the response object from Google Login inline
interface GoogleLoginResponse {
  credential?: string;
  clientId?: string;
  select_by?: string;
}

const CLIENT_ID = import.meta.env.VITE_CLIENT_ID
console.log(CLIENT_ID)

const Login: React.FC = () => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Parameter is typed to our inline interface
  const handleLoginSuccess = async (credentialResponse: GoogleLoginResponse): Promise<void> => {
    const idToken = credentialResponse.credential;

    if (!idToken) {
      setError("Failed to retrieve ID token from Google.");
      return;
    }

    try {
      setError(null);
      // Send the token to the FastAPI backend
      const response = await fetch("http://localhost:8000/api/auth/google", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          credential: idToken,
        }),
      });

      if (!response.ok) {
        throw new Error("Backend authentication failed");
      }

      const data = await response.json();
      setUser(data.user as UserProfile);
    } catch (err) {
      console.error("Error logging in:", err);
      setError("Could not log in with backend. Please try again.");
    }
  };

  const handleLoginFailure = (): void => {
    console.error("Google Login Failed");
    setError("Google authentication failed.");
  };

  const handleLogout = (): void => {
    setUser(null);
    setError(null);
  };

  return (
    <GoogleOAuthProvider clientId={CLIENT_ID}>
      <div style={{ textAlign: 'center', marginTop: '50px', fontFamily: 'Arial, sans-serif' }}>
        <h2>FastAPI + React Google OAuth (TSX)</h2>
        
        {error && <p style={{ color: 'red' }}>{error}</p>}
        
        {!user ? (
          <div style={{ display: 'inline-block', marginTop: '20px' }}>
            <GoogleLogin
              onSuccess={handleLoginSuccess}
              onError={handleLoginFailure}
            />
          </div>
        ) : (
          <div style={{ marginTop: '20px' }}>
            <h3>Welcome, {user.name}!</h3>
            <p>Email: {user.email}</p>
            {user.picture && (
              <img 
                src={user.picture} 
                alt={`${user.name}'s profile`} 
                style={{ borderRadius: '50%', width: '100px', height: '100px' }} 
              />
            )}
            <br />
            <button 
              onClick={handleLogout} 
              style={{ 
                marginTop: '20px', 
                padding: '10px 20px', 
                fontSize: '16px', 
                cursor: 'pointer' 
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>
    </GoogleOAuthProvider>
  );
};

export default Login
