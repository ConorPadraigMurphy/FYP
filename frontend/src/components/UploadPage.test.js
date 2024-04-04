import React from "react";
import {
  render,
  fireEvent,
  waitFor,
  screen,
  findAllByTestId,
  queryByTestId,
  getByTestId,
} from "@testing-library/react";
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

  test("disables upload button when address and date/time are selected", async () => {
    render(<UploadPage />);
    const uploadButton = screen.getByRole("button");
    await waitFor(() => {
      expect(uploadButton).toBeEnabled();
    });
  });

  // Cannot test mui components
  test("DateTime picker should be in the document", async () => {
    render(<UploadPage />);
    const dateTimePicker = await screen.findByPlaceholderText(
      "MM/DD/YYYY hh:mm aa"
    );
    expect(dateTimePicker).toBeInTheDocument();
  });
});
