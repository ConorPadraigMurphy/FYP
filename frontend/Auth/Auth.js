const User = require("../model/User")

// Validations of register data and create or error
exports.register = async (req, res, next) => {
    const { username, password } = req.body
    if (password.length < 6) {
        return res.status(400).json({ message: "Password less than 6 characters" })
    }
    try {
        await User.create({
            username,
            password,
        }).then(user =>
            res.status(200).json({
                message: "User successfully created",
                user,
            })
        )
    } catch (err) {
        res.status(401).json({
            message: "User not successfully created",
            error: err.message,
        });
    }
}

// Looks for user in the user db using details with validation
exports.login = async (req, res, next) => {
    const { username, password } = req.body;
    try {
        const user = await User.findOne({ username, password })
        if (!user) {
            res.status(401).json({
                message: "Login not successful",
                error: "User not found",
            })
        } else {
            res.status(200).json({
                message: "Login successful",
                user,
            })
        }
    } catch (error) {
        res.status(400).json({
            message: "An error occurred",
            error: error.message,
        })
    }
}

// Finds user by id and deletes user
exports.deleteUser = async (req, res, next) => {
    const { id } = req.body;
    try {
        const user = await User.findOneAndDelete({ _id: id });
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }
        res.status(201).json({ message: "User successfully deleted", user });
    } catch (error) {
        res.status(400).json({ message: "An error occurred", error: error.message });
    }
};

