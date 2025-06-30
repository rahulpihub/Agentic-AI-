import { Routes, Route } from 'react-router-dom'
import Home from './Home'
import Verification from './Verification'

function App() {
    return (
        <div>
            {/* Route Mapping */}
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/approval" element={<Verification />} />
            </Routes>
        </div>
    )
}

export default App
