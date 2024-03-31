import React, { useState } from "react";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import { CardActions, Typography, Link } from "@mui/material";
import trafficCoverImage from "../images/TrafficCover.png";
import axios from "axios";
import { Snackbar, Alert } from "@mui/material";
import { useNavigate } from "react-router-dom";

function LoginPage() {
  // State variables for storing username, password, snackbar status, message, and severity
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState("");
  const [snackbarSeverity, setSnackbarSeverity] = useState("success");
  const navigate = useNavigate();

  // Function to handle form submission
  const handleSubmit = async (event) => {
    event.preventDefault();

    try {
      // Sending login request to the server
      const response = await axios.post(
        "http://localhost:3001/api/auth/login",
        {
          username,
          password,
        }
      );

      console.log("Login successful", response.data);

      setSnackbarMessage("Logged in successfully. Please wait...");
      setOpenSnackbar(true);

      // Delay before redirecting
      setTimeout(() => {
        // Redirecting to the login page upon successful signup
        navigate("/upload");
      }, 2000);
    } catch (error) {
      // Handling login error
      console.error("Login error:", error);
      setSnackbarMessage(
        "Login failed: " + (error.response?.data?.message || error.message)
      );
      setSnackbarSeverity("error");
      setOpenSnackbar(true);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        backgroundSize: "cover",
        backgroundImage: `url(${trafficCoverImage})`,
      }}
    >
      {/* Right Div */}
      <div style={{ flex: 1 }}>
        <Card
          sx={{
            maxWidth: 500,
            maxHeight: 600,
            margin: "auto",
            marginTop: "30vh",
            borderRadius: "12px",
            backgroundColor: "rgb(45,45,48)",
            color: "white",
          }}
        >
          <form onSubmit={handleSubmit}>
            <CardContent style={{ margin: "15px" }}>
              <Typography variant="h6" component="h6" sx={{ color: "white" }}>
                Sign In
              </Typography>
              {/* Username input field */}
              <TextField
                label="Username"
                variant="outlined"
                fullWidth
                margin="normal"
                InputLabelProps={{ style: { color: "white" } }}
                InputProps={{
                  style: { color: "white" },
                  notchedOutline: { borderColor: "white" },
                }}
                onChange={(e) => setUsername(e.target.value)}
              />
              {/* Password input field */}
              <TextField
                label="Password"
                variant="outlined"
                fullWidth
                margin="normal"
                type="password"
                InputLabelProps={{ style: { color: "white" } }}
                InputProps={{
                  style: { color: "white" },
                  notchedOutline: { borderColor: "white" },
                }}
                onChange={(e) => setPassword(e.target.value)}
              />
              {/* Link to sign up page */}
              <Typography
                variant="body2"
                style={{ marginTop: "16px", color: "white" }}
              >
                Don't have an account?{" "}
                <Link
                  href={process.env.REACT_APP_PUBLIC_URL + "/signup"}
                  sx={{ color: "#90caf9" }}
                >
                  Sign up
                </Link>
              </Typography>
            </CardContent>
            {/* Submit button */}
            <CardActions style={{ margin: "15px" }}>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{
                  backgroundColor: "primary.main",
                  "&:hover": { backgroundColor: "primary.dark" },
                }}
              >
                Log In
              </Button>
            </CardActions>
          </form>
        </Card>
      </div>
      {/* Snackbar for displaying login status */}
      <Snackbar
        open={openSnackbar}
        autoHideDuration={6000}
        onClose={() => setOpenSnackbar(false)}
      >
        <Alert
          onClose={() => setOpenSnackbar(false)}
          severity={snackbarSeverity}
          sx={{ width: "100%" }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </div>
  );
}

export default LoginPage;
