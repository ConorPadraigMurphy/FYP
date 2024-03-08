import React, { useState } from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { CardActions, Typography, Link } from '@mui/material';
import trafficCoverImage from '../images/TrafficCover.png';


function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = (event) => {
        event.preventDefault();
        console.log(username, password);
    };

    return (

        <div style={{
            display: 'flex', height: '100vh', backgroundSize: 'cover', backgroundImage: `url(${trafficCoverImage})`,
        }}>
            
            {/* Right Div */}
            <div style={{ flex: 1 }}>
                <Card 
    sx={{ 
        maxWidth: 500, 
        maxHeight: 500, 
        margin: 'auto', 
        marginTop: '30vh',
        borderRadius: '12px',
        backgroundColor: 'rgb(45,45,48)', 
        color: 'white',
    }}
>
    <form onSubmit={handleSubmit}>
        <CardContent>
            <Typography variant="h6" component="h6" sx={{ color: 'white' }}>Sign In</Typography>
            <TextField
                label="Username"
                variant="outlined"
                fullWidth
                margin="normal"
                InputLabelProps={{ style: { color: 'white' } }}
                InputProps={{
                    style: { color: 'white' },
                    notchedOutline: { borderColor: 'white' }
                }}
                onChange={(e) => setUsername(e.target.value)}
            />
            <TextField
                label="Password"
                variant="outlined"
                fullWidth
                margin="normal"
                type="password"
                InputLabelProps={{ style: { color: 'white' } }}
                InputProps={{
                    style: { color: 'white' },
                    notchedOutline: { borderColor: 'white' }
                }}
                onChange={(e) => setPassword(e.target.value)}
            />
            <Typography variant="body2" style={{ marginTop: '16px', color: 'white' }}>
                Don't have an account? <Link href="/signup" sx={{ color: '#90caf9' }}>Sign up</Link>
            </Typography>
        </CardContent>
        <CardActions>
            <Button type="submit" fullWidth variant="contained" sx={{ backgroundColor: 'primary.main', '&:hover': { backgroundColor: 'primary.dark' } }}>
                Log In
            </Button>
        </CardActions>
    </form>
</Card>

            </div>
        </div>

    );
}

export default LoginPage;
