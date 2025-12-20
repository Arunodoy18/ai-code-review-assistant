import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import RunDetail from './pages/RunDetail'
import Projects from './pages/Projects'
import Configuration from './pages/Configuration'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/runs/:runId" element={<RunDetail />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/configuration" element={<Configuration />} />
      </Routes>
    </Layout>
  )
}

export default App
