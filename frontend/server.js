const express = require("express");
const mongoose = require("mongoose");

const app = express();
const PORT = 3001;

// Use environment variables for sensitive information
const MONGODB_URI =
  "mongodb+srv://admin:admin@cluster0.rhqvnnf.mongodb.net/FYP";

// Connect to MongoDB
mongoose.connect(MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});

// Define the vehicle schema
const vehicleSchema = new mongoose.Schema({
  object_id: Number,
  class_id: String,
  entered_time: Number,
  exited_time: Number,
  direction: String,
});

// Create a mongoose model
const Vehicle = mongoose.model("Vehicle", vehicleSchema);

// Express route to get vehicle data
app.get("/api/vehicleData", async (req, res) => {
  try {
    // Fetch all vehicle data from MongoDB
    const vehicleData = await Vehicle.find();
    res.json(vehicleData);
  } catch (error) {
    console.error("Error fetching vehicle data:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
