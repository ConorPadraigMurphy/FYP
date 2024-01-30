import React from 'react';
import axios from 'axios';

class UploadPage extends React.Component {
    render() {
        return (
            <div className="home-page-content">
                <h2>Welcome to Our Site!</h2>
                <input type="file" accept="video/*" onChange={this.handleVideoUpload} />
            </div>
        );
    }

    handleVideoUpload = (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        const formData = new FormData();
        formData.append('file', file);  

        axios.post('http://127.0.0.1:5000/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        }).then(response => {
            console.log('Video uploaded successfully', response.data);
            // Handle response here
        }).catch(error => {
            console.error('Error uploading video', error);
        });
    }
}

export default UploadPage;
