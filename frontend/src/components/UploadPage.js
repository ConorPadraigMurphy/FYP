import React from 'react';
import axios from 'axios';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const VisuallyHiddenInput = styled('input')({
    clip: 'rect(0 0 0 0)',
    clipPath: 'inset(50%)',
    height: 1,
    overflow: 'hidden',
    position: 'absolute',
    bottom: 0,
    left: 0,
    whiteSpace: 'nowrap',
    width: 1,
});

const CenteredContainer = styled('div')({
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'column',
    height: '25vh',
});

class UploadPage extends React.Component {
    state = {
        uploadStatus: null
    };

    render() {
        return (
            <CenteredContainer>
                <Button
                    component="label"
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                >Upload Video
                    <VisuallyHiddenInput
                        type="file"
                        accept="video/*"
                        onChange={this.handleVideoUpload}
                    />
                </Button>
                {this.state.uploadStatus && (
                    <p style={{ color: this.state.uploadStatus === 'success' ? 'green' : 'red' }}>
                        {this.state.uploadStatus === 'success'
                            ? 'Video uploaded successfully!'
                            : 'Error uploading video. Please try again.'}
                    </p>
                )}
            </CenteredContainer>
        );
    }

    handleVideoUpload = (event) => {
        const file = event.target.files[0];
        if (!file) {
            this.setState({ videoSelected: false, uploadStatus: null });
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        axios
            .post('http://127.0.0.1:5000/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            })
            .then((response) => {
                console.log('Video uploaded successfully', response.data);
                this.setState({ videoSelected: true, uploadStatus: 'success' });
            })
            .catch((error) => {
                console.error('Error uploading video', error);
                this.setState({ videoSelected: true, uploadStatus: 'error' });
            });
    };
}

export default UploadPage;
