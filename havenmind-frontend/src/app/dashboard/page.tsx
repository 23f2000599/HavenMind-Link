import Navbar from '@/components/Navbar'

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Mental Health Dashboard</h1>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold text-lg mb-2">Cognitive Load Index</h3>
            <div className="text-3xl font-bold text-green-600">72%</div>
            <p className="text-sm text-gray-600">Moderate stress level</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold text-lg mb-2">Mood Trend</h3>
            <div className="text-3xl font-bold text-blue-600">↗️</div>
            <p className="text-sm text-gray-600">Improving this week</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="font-semibold text-lg mb-2">Support Network</h3>
            <div className="text-3xl font-bold text-purple-600">5</div>
            <p className="text-sm text-gray-600">Active peer connections</p>
          </div>
        </div>
      </div>
    </div>
  )
}