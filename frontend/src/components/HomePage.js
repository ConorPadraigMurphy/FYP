import * as React from "react";
import Card from "@mui/material/Card";
import CardActions from "@mui/material/CardActions";
import CardContent from "@mui/material/CardContent";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";

function CardComponent({ title, category, content }) {
  return (
    <Card variant="outlined">
      <CardContent>
        <Typography sx={{ fontSize: 16 }} color="text.primary" gutterBottom>
          <u><b>{category}</b></u>
        </Typography>
        <Typography variant="h5" component="div">
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {content}
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small">Read More</Button>
      </CardActions>
    </Card>
  );
}

export default function GridOfTrafficCards() {
  return (
    <Grid container spacing={2} sx={{ padding: 2 }}>
      <Grid item xs={12} sm={6} md={4}>
        <CardComponent
          title="Traffic Congestion on Main Street"
          category="Traffic News"
          content="Expect delays due to heavy traffic on Main Street during rush hours."
        />
      </Grid>

      <Grid item xs={12} sm={6} md={4}>
        <CardComponent
          title="New Traffic Regulations in Effect"
          category="Regulatory Update"
          content="Stay informed about the latest traffic regulations to ensure compliance."
        />
      </Grid>

      <Grid item xs={12} sm={6} md={4}>
        <CardComponent
          title="Avoiding Traffic Jams: Tips for Commuters"
          category="Tips and Tricks"
          content="Discover effective strategies to avoid traffic jams and reach your destination faster."
        />
      </Grid>
    </Grid>
  );
}
