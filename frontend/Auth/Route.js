const express = require("express")
const router = express.Router()
const { register } = require("./Auth")

//http://localhost:3001/api/auth/register

// Pass in body JSON to test{
//    "username": "test1",
//    "password": "123567"
// }
router.route("/register").post(register)

module.exports = router