import React from 'react';
import axios from 'axios';
import { styled } from '@mui/material/styles';
import Button from '@mui/material/Button';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { GoogleMap, LoadScript, StandaloneSearchBox, Marker } from '@react-google-maps/api';

// Styles for visually hidden input for accessibility
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

// Container styling for centered layout
const CenteredContainer = styled('div')({
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    flexDirection: 'column',
    height: '100vh',
});

const libraries = ['places']; // Required for places input (autocomplete)

const mapContainerStyle = {
    height: '400px',
    width: '800px'
};

class UploadPage extends React.Component {
    state = {
        uploadStatus: null, // Track the upload status
        selectedAddress: null, // Store the selected address from search
        mapCenter: {
            lat: 53.349805,
            lng: -6.26031  
        },
        markerPosition: null // Store marker position for user-selected location
    };

    // Callback when the search box component is loaded
    onSearchBoxLoaded = ref => {
        this.searchBox = ref;
    };

    // Handle the selection of a place using the search box
    onPlacesChanged = () => {
        const places = this.searchBox.getPlaces();
        if (places && places.length > 0) {
            const location = places[0].geometry.location;
            // Update state with the selected address and move map & marker to that location
            this.setState({
                selectedAddress: places[0]?.formatted_address || 'No address selected',
                mapCenter: {
                    lat: location.lat(),
                    lng: location.lng()
                },
                markerPosition: {
                    lat: location.lat(),
                    lng: location.lng()
                }
            });
        }
    };

    // Handle map click to allow user to drop a pin
    onMapClick = (event) => {
        // Update the marker position based on where the user clicked on the map
        this.setState({
            markerPosition: {
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            },
            mapCenter: {
                lat: event.latLng.lat(),
                lng: event.latLng.lng()
            }
        });
    };

    // Render the map with a search box and a marker for the selected location
    renderMap() {
        return (
            <LoadScript
                googleMapsApiKey="AIzaSyBJ39gTzB4yRuN_JTevio4hEcJYSgM8B3o"
                libraries={libraries}
            >
                <GoogleMap
                    mapContainerStyle={mapContainerStyle}
                    center={this.state.mapCenter}
                    zoom={10}
                    onClick={this.onMapClick} // Allow user to click on the map to drop a pin
                >
                    <StandaloneSearchBox
                        onLoad={this.onSearchBoxLoaded}
                        onPlacesChanged={this.onPlacesChanged}
                    >
                        <input
                            type="text"
                            placeholder="Search for places..."
                            style={{
                                boxSizing: `border-box`,
                                border: `1px solid transparent`,
                                width: `240px`,
                                height: `32px`,
                                padding: `0 12px`,
                                borderRadius: `3px`,
                                boxShadow: `0 2px 6px rgba(0, 0, 0, 0.3)`,
                                fontSize: `14px`,
                                outline: `none`,
                                textOverflow: `ellipses`,
                                position: "absolute",
                                left: "50%",
                                marginLeft: "-120px"
                            }}
                        />
                    </StandaloneSearchBox>
                    {this.state.markerPosition && (
                        <Marker
                            position={this.state.markerPosition} // Show marker at selected or clicked location
                        />
                    )}
                </GoogleMap>
            </LoadScript>
        );
    }

    render() {
        return (
            <CenteredContainer>
                {this.renderMap()}
                <Button
                    component="label"
                    variant="contained"
                    startIcon={<CloudUploadIcon />}
                >
                    Upload Video
                    <VisuallyHiddenInput
                        type="file"
                        accept="video/*"
                        onChange={this.handleVideoUpload} // Handle file selection for upload
                    />
                </Button>
                {this.state.uploadStatus && (
                    <p style={{ color: this.state.uploadStatus === 'success' ? 'green' : 'red' }}>
                        {this.state.uploadStatus === 'success'
                            ? 'Video uploaded successfully!'
                            : 'Error uploading video. Please try again.'}
                    </p>
                )}
                {this.state.selectedAddress && (
                    <p>Selected Address: {this.state.selectedAddress}</p> // Display the selected address
                )}
            </CenteredContainer>
        );
    }

    // Handle the video file upload
    handleVideoUpload = (event) => {
        const file = event.target.files[0];
        if (!file) {
            this.setState({ uploadStatus: null });
            return;
        }

        const formData = new FormData();
        formData.append('file', file); // Add the video file to the form data
        if (this.state.selectedAddress) {
            formData.append('address', this.state.selectedAddress); // Include the selected address if available
        }

        // Perform the upload via axios
        axios.post('http://127.0.0.1:5000/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
            .then((response) => {
                console.log('Video and address uploaded successfully', response.data);
                this.setState({ uploadStatus: 'success' }); // Update upload status on success
            })
            .catch((error) => {
                console.error('Error uploading video and address', error);
                this.setState({ uploadStatus: 'error' }); // Update upload status on failure
            });
    };
}

export default UploadPage;
