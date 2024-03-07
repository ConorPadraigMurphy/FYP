const express = require("express")
const router = express.Router()
const { register, login } = require("./Auth")

//Register route
//http://localhost:3001/api/auth/register

// Pass in body JSON to test{
//    "username": "test1",
//    "password": "123567"
// }
router.route("/register").post(register)

//Login route
//http://localhost:3001/api/auth/login

// Pass in body JSON to test{
//    "username": "test1",
//    "password": "123567"
// }
router.route("/login").post(login);

module.exports = router;