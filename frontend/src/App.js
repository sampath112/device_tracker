



import React, { useState, useEffect } from "react";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import "./App.css";

function App() {
  const [username, setUsername] = useState("");
  const [deviceId, setDeviceId] = useState(localStorage.getItem("deviceId") || "");
  const [devices, setDevices] = useState([]);
  const [message, setMessage] = useState("");

  // Generate or retrieve device ID
  const getDeviceId = () => {
    if (!deviceId) {
      const newDeviceId = uuidv4();
      localStorage.setItem("deviceId", newDeviceId);
      setDeviceId(newDeviceId);
      return newDeviceId;
    }
    return deviceId;
  };

  // Detect device type (mobile or desktop)
  const isMobile = () => /Mobi|Android/i.test(navigator.userAgent);

  // Handle login
  const handleLogin = async (e) => {
    e.preventDefault();
    const payload = { username, device_id: getDeviceId(), device_type: isMobile() ? "mobile" : "desktop" };
    console.log("Sending login request:", payload);
    try {
      const response = await axios.post(
        "http://localhost:8000/api/login",
        payload,
        { headers: { "Content-Type": "application/json", "Accept": "application/json" } }
      );
      setMessage(response.data.message);
      fetchDevices();
    } catch (error) {
      console.error("Login error:", {
        message: error.message,
        response: error.response,
        request: error.request,
        config: error.config,
      });
      setMessage(
        error.response?.data?.error ||
        `Login failed: ${error.message}. Check console for details.`
      );
    }
  };

  // Fetch devices
  const fetchDevices = async () => {
    if (!username) return;
    console.log("Fetching devices for:", username);
    try {
      const response = await axios.get(`http://localhost:8000/api/devices/${username}`);
      setDevices(response.data.devices);
    } catch (error) {
      console.error("Fetch devices error:", {
        message: error.message,
        response: error.response,
        request: error.request,
        config: error.config,
      });
      setMessage(
        error.response?.data?.error ||
        `Failed to fetch devices: ${error.message}. Check console.`
      );
    }
  };

  return (
    <div className="App">
      <h1>Device Tracker</h1>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
      <p>{message}</p>
      {devices.length > 0 && (
        <div>
          <h2>Devices for {username}</h2>
          <table>
            <thead>
              <tr>
                <th>Device ID</th>
                <th>Device Type</th>
                <th>Last Login</th>
                <th>Login Count</th>
              </tr>
            </thead>
            <tbody>
              {devices.map((device, index) => (
                <tr key={index}>
                  <td>{device.device_id}</td>
                  <td>{device.device_type || "Unknown"}</td>
                  <td>{new Date(device.last_login).toLocaleString()}</td>
                  <td>{device.login_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default App;