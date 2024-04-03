import React from "react";
import { render, fireEvent, waitFor, screen } from "@testing-library/react";
import UploadPage from "./UploadPage";

// Mock axios post method
jest.mock("axios", () => ({
  post: jest.fn(() => Promise.resolve({ data: "mocked response" })),
}));

describe("UploadPage", () => {
  test("renders without crashing", () => {
    render(<UploadPage />);
    expect(
      screen.getByText("Select the date & time the video was recorded:")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Select the location that the video was recorded:")
    ).toBeInTheDocument();
  });

  test("enables upload button when address and date/time are selected", async () => {
    render(<UploadPage />);
    const uploadButton = screen.getByText("Upload Video");
    const dateTimePicker = screen.getByRole("textbox");
    fireEvent.change(dateTimePicker, {
      target: { value: "2024-04-03T12:00:00" },
    });
    await waitFor(() => {
      expect(uploadButton).toBeEnabled();
    });
  });

  test("DateTime picker should be in the document", () => {
    const { getByTestId } = render(<UploadPage />);
    const dateTimePicker = getByTestId("date-time-picker");
    expect(dateTimePicker).toBeInTheDocument();
  });

  test("Map should be in the document", () => {
    const { getByTestId } = render(<UploadPage />);
    const map = getByTestId("map");
    expect(map).toBeInTheDocument();
  });
});
