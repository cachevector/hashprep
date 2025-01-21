# HashPrep Frontend

This is the **frontend** of the HashPrep platform, built using **Bun** and **Next.js**. It provides a user-friendly interface for technical interview preparation, featuring study plans, coding challenges, and progress tracking.

## Project Structure

- **public/**: Contains static files like images, fonts, and other assets.
- **src/**: The source code of the frontend, including components, pages, and styles.
  - **components/**: Reusable React components for the UI.
  - **app/**: Next.js pages for routing and view management.
  - **styles/**: Global CSS/SCSS files to style the frontend.
  - **lib/**: Utility functions, custom hooks, and helpers.
- **package.json**: Frontend dependencies and scripts.
- **tsconfig.json**: TypeScript configuration for frontend.
- **README.md**: Documentation specific to the frontend project.

## Getting Started

### 1. Install Dependencies

Navigate to the `frontend` directory and install the necessary dependencies:

  - Run `bun install` to install the frontend dependencies.

### 2. Run the Application

To start the frontend in development mode:

- Run `bun dev` to start the development server.
- This will run the Next.js application at `http://localhost:3000`.

### 3. Build for Production

Once you're ready to build the application for production:

- Run `bun build` to build the Next.js application for production deployment.

## Contributing

Contributions to the frontend are always welcome! Whether it’s adding new features, fixing bugs, or improving the UI, feel free to fork the repository and submit a pull request.

Please follow the contributing guidelines in the root `README.md`.

## License

This project is licensed under the MIT License.
