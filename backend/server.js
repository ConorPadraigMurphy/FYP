const express = require("express");
const app = express();
const bodyParser = require("body-parser");
const cors = require("cors");
const mongoose = require("mongoose");
const port = 3001;
require("dotenv").config({ path: "../.env" });

// Use environment variables for sensitive information
const MONGO_URI = process.env.MONGO_API_KEY;

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(cors());

// Allows to take in JSON for login details
app.use(express.json());

// import your route.js
app.use("/api/auth", require("./Auth/Route"));

mongoose.set("strictQuery", true);

// Connect to MongoDB
async function main() {
  await mongoose.connect(MONGO_URI, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  });
  console.log("Connected to MongoDB successfully");
}

main().catch((err) => console.log(err));

// Define the vehicle schema
const vehicleSchema = new mongoose.Schema({
  object_id: Number,
  class_id: String,
  entered_time: Number,
  exited_time: Number,
  direction: String,
  timestamp: Number,
  address: String,
});

// Create a mongoose model
const Vehicle = mongoose.model("vehicles", vehicleSchema, "FYP");

// Express route to get vehicle data
app.get("/api/vehicleData", async (req, res) => {
  try {
    // Fetch all vehicle data from MongoDB
    const data = await Vehicle.find({});
    console.log("Data retrieved:", data);
    res.json(data);
  } catch (error) {
    console.error("Error fetching vehicle data:", error);
    res.status(500).json({ error: "Internal Server Error" });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
