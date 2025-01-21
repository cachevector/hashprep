import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, Heart } from "lucide-react"
import { firaSans } from "@/app/ui/fonts"

export default function ComingSoonPage() {
  return (
    <div className={`min-h-screen flex flex-col bg-gray-50 text-black ${firaSans.className}`}>
      <main className="flex-grow flex flex-col items-center justify-center p-4 md:p-6 space-y-8">
        {/* Home page content */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-violet-600 mb-4">Welcome to #HashPrep;</h1>
          <p className="text-xl text-gray-700">Your ultimate platform for Interview Preparation</p>
        </div>

        {/* Coming soon card */}
        <Card className="w-full max-w-md bg-white shadow-xl rounded-[0.5rem] border-violet-100">
          <CardHeader className="space-y-4">
            <CardTitle className="text-4xl md:text-5xl font-extrabold text-center bg-gradient-to-r from-violet-600 to-violet-500 bg-clip-text text-transparent leading-tight py-1">
              Coming Soon
            </CardTitle>
            <CardDescription className="text-center text-lg text-gray-600">
              Your journey to interview success starts here
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-8">
            <p className="text-center text-gray-700 text-lg leading-relaxed">
              HashPrep is crafting a revolutionary platform to transform your interview preparation journey. Get ready
              to experience a smarter way to prepare and succeed!
            </p>
            <div className="space-y-4">
              <h3 className="font-semibold text-xl text-violet-900 mb-4">What to expect:</h3>
              <ul className="space-y-4">
                {[
                  {
                    title: "Track your progress",
                    description: "Monitor your growth with detailed analytics and insights",
                  },
                  {
                    title: "Personalized study plans",
                    description: "Custom-tailored learning paths based on your goals",
                  },
                  {
                    title: "Mock interviews",
                    description: "Practice with real-world scenarios and expert feedback",
                  },
                  {
                    title: "Comprehensive resources",
                    description: "Access curated materials and proven strategies",
                  },
                ].map((feature, index) => (
                  <li key={index} className="flex items-start space-x-3 group">
                    <CheckCircle className="text-violet-600 w-5 h-5 mt-1 flex-shrink-0 group-hover:text-violet-500 transition-colors" />
                    <div>
                      <h4 className="font-medium text-gray-900 group-hover:text-violet-600 transition-colors">
                        {feature.title}
                      </h4>
                      <p className="text-gray-600 text-sm">{feature.description}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </CardContent>
        </Card>
      </main>

      <footer className="p-4 md:p-6 text-center text-gray-600">
        <p className="flex items-center justify-center gap-1">
          Made with <Heart className="text-red-500 w-4 h-4 inline" fill="currentColor" /> by Aftaab Siddiqui
        </p>
        <p className="mt-2">&copy; {new Date().getFullYear()} HashPrep. All rights reserved.</p>
      </footer>
    </div>
  )
}

