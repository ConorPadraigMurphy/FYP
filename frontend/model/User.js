const Mongoose = require("mongoose")

// User login schema
const UserSchema = new Mongoose.Schema({
    username: {
        type: String,
        unique: true,
        required: true,
    },
    password: {
        type: String,
        minlength: 6,
        required: true,
    }
})

const User = Mongoose.model("user", UserSchema)
module.exports = User