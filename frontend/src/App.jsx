import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Compare from './pages/Compare';
import Forensics from './pages/Forensics';
import Benchmark from './pages/Benchmark';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/forensics" element={<Forensics />} />
          <Route path="/benchmark" element={<Benchmark />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
