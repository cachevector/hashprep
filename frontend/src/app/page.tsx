import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle } from "lucide-react"
import { firaSans } from "@/app/ui/fonts"

export default function ComingSoonPage() {
  return (
    <div className={`min-h-screen flex flex-col bg-gray-50 text-black ${firaSans.className}`}>
      <header className="p-4 md:p-6">
        <h1 className="text-2xl md:text-3xl font-bold text-violet-600">#HashPrep;</h1>
      </header>

      <main className="flex-grow flex items-center justify-center p-4 md:p-6">
        <Card className="w-full max-w-md bg-gray-100 shadow-xl rounded-[0.5rem]">
          <CardHeader>
            <CardTitle className="text-3xl md:text-4xl font-extrabold text-center text-black">Coming Soon</CardTitle>
            <CardDescription className="text-center text-gray-600">
              Your ultimate platform for Interview Preparation
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-center text-gray-700">
              HashPrep is gearing up to revolutionize how you prepare for interviews. Stay tuned and be the first to
              know when we launch!
            </p>
            <form className="space-y-2">
              <Input
                type="email"
                placeholder="Enter your email"
                className="border-violet-300 placeholder-violet-400 rounded-[0.5rem]"
              />
              <Button className="w-full bg-violet-600 hover:bg-violet-700 text-white rounded-[0.5rem]">
                Notify Me
              </Button>
            </form>
            <div className="space-y-2">
              <h3 className="font-semibold text-black">What to expect:</h3>
              <ul className="space-y-1">
                {["Track your progress", "Personalized study plans", "Mock interviews", "Comprehensive resources"].map(
                  (feature, index) => (
                    <li key={index} className="flex items-center space-x-2">
                      <CheckCircle className="text-violet-600" size={16} />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ),
                )}
              </ul>
            </div>
          </CardContent>
        </Card>
      </main>

      <footer className="p-4 md:p-6 text-center text-gray-600">
        <p>&copy; {new Date().getFullYear()} HashPrep. All rights reserved.</p>
      </footer>
    </div>
  )
}

