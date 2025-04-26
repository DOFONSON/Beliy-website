import React from 'react';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import ArticleList from './components/ArticleList';

const theme = createTheme({
  palette: {
    mode: 'light',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <ArticleList />
    </ThemeProvider>
  );
}

export default App;