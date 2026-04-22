/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { motion } from "motion/react";
import { Layers, Rocket, Code2, Sparkles, Plus, Monitor, Send } from "lucide-react";

export default function App() {
  return (
    <div className="min-h-screen bg-[#F4F4F5] text-[#1a1a1a] font-sans selection:bg-blue-600 selection:text-white flex flex-col">
      {/* Header - Geometric Balance Style */}
      <header className="h-16 bg-white border-b border-gray-200 px-8 flex items-center justify-between z-50 sticky top-0">
        <div className="flex items-center gap-4">
          <div className="w-8 h-8 bg-blue-600 rounded-md flex items-center justify-center">
            <div className="w-4 h-4 bg-white rounded-sm"></div>
          </div>
          <span className="font-semibold text-gray-900 tracking-tight text-lg">Studio.Boilerplate</span>
        </div>
        <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-gray-500">
          <a href="#" className="text-blue-600 border-b-2 border-blue-600 py-5">Editor</a>
          <a href="#" className="hover:text-gray-900 transition-colors">Assets</a>
          <a href="#" className="hover:text-gray-900 transition-colors">Settings</a>
        </nav>
        <div className="flex items-center gap-4">
          <button className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium border border-gray-200 hover:bg-gray-200 transition-colors">
            <Monitor className="w-4 h-4" /> Preview
          </button>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium shadow-sm hover:bg-blue-700 transition-all active:scale-95 flex items-center gap-2">
            <Send className="w-4 h-4" /> Publish
          </button>
        </div>
      </header>

      {/* Main Content Layout */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Sidebar Pattern (Simulated) */}
        <aside className="hidden lg:flex w-64 bg-white border-r border-gray-200 flex-col">
          <div className="p-4 border-b border-gray-100 flex justify-between items-center">
            <span className="text-xs font-bold text-gray-400 uppercase tracking-widest">Components</span>
            <button className="text-gray-400 hover:text-gray-600"><Plus className="w-4 h-4" /></button>
          </div>
          <div className="flex-1 p-2 space-y-1">
            <div className="p-2 bg-blue-50 text-blue-700 rounded-md text-sm flex items-center font-medium">
              <Layers className="w-4 h-4 mr-2" /> Hero Section
            </div>
            <div className="p-2 text-gray-600 rounded-md text-sm flex items-center hover:bg-gray-50 cursor-pointer">
              <Code2 className="w-4 h-4 mr-2" /> Features Grid
            </div>
          </div>
        </aside>

        {/* Center Canvas Area */}
        <div className="flex-1 bg-[#EBEDF0] p-4 md:p-12 flex flex-col items-center justify-center relative overflow-auto">
          {/* Grid Background */}
          <div className="absolute inset-0 opacity-5 pointer-events-none bg-grid"></div>
          
          {/* Main Card Area - Original Content Preserved inside themed container */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="w-full max-w-4xl min-h-[500px] bg-white rounded-xl shadow-2xl border border-gray-300 flex flex-col items-center justify-center p-8 md:p-16 text-center relative z-10"
          >
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-[10px] font-bold uppercase tracking-wider text-blue-600 mb-8 border border-blue-100">
                <Sparkles className="w-3 h-3" /> Geometric Balancing
              </span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="text-4xl md:text-6xl font-bold tracking-tight mb-8 max-w-3xl leading-[1.1] text-gray-900"
            >
              Khám phá sức mạnh của <br />
              <span className="text-blue-600">Sự Cân Bằng Hình Học.</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-base md:text-lg text-gray-500 mb-12 max-w-xl leading-relaxed"
            >
              Chào mừng đến với phiên bản được nâng cấp giao diện. Chúng tôi đã áp dụng phong cách thiết kế phòng làm việc chuyên nghiệp, giúp bạn tập trung vào những gì quan trọng nhất.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl"
            >
              <div className="p-6 bg-gray-50 border border-gray-200 border-dashed rounded-2xl hover:border-blue-400 transition-colors text-left group">
                <div className="w-10 h-10 bg-white border border-gray-200 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-all shadow-sm">
                  <Code2 className="w-5 h-5" />
                </div>
                <h3 className="font-bold mb-2 text-gray-900">Thiết kế Kỹ thuật</h3>
                <p className="text-xs text-gray-500">Mọi yếu tố đều được tính toán theo tỷ lệ vàng và lưới hình học.</p>
              </div>

              <div className="p-6 bg-gray-50 border border-gray-200 border-dashed rounded-2xl hover:border-blue-400 transition-colors text-left group">
                <div className="w-10 h-10 bg-white border border-gray-200 rounded-xl flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-all shadow-sm">
                  <Rocket className="w-5 h-5" />
                </div>
                <h3 className="font-bold mb-2 text-gray-900">Tăng tốc Dự án</h3>
                <p className="text-xs text-gray-500">Cấu trúc rõ ràng giúp việc mở rộng và bảo trì dự án trở nên dễ dàng hơn.</p>
              </div>
            </motion.div>
          </motion.div>
          
          {/* Tool Overlay Effect */}
          <div className="mt-8 bg-white px-6 py-3 rounded-full shadow-lg border border-gray-200 flex space-x-8 text-xs font-bold uppercase tracking-widest text-gray-400">
            <button className="hover:text-blue-600 transition-colors">Structure</button>
            <button className="text-blue-600">Canvas</button>
            <button className="hover:text-blue-600 transition-colors">Style</button>
          </div>
        </div>

        {/* Right Sidebar Pattern (Simulated) */}
        <aside className="hidden xl:flex w-72 bg-white border-l border-gray-200 flex-col">
          <div className="p-4 border-b border-gray-100 font-bold text-xs text-gray-400 uppercase tracking-widest">
            Properties
          </div>
          <div className="p-6 space-y-6">
            <div>
              <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-2">Theme Balance</label>
              <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div className="h-full bg-blue-600 w-[65%]"></div>
              </div>
            </div>
            <div className="pt-4 border-t border-gray-50">
              <label className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block mb-3">Status</label>
              <div className="flex items-center justify-between text-xs font-medium text-gray-600">
                <span>Rendering</span>
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              </div>
            </div>
          </div>
        </aside>
      </main>

      {/* Footer Status Bar */}
      <footer className="h-10 bg-white border-t border-gray-200 px-6 flex items-center justify-between">
        <div className="flex items-center space-x-4 text-[10px] uppercase tracking-widest font-bold text-gray-400">
          <span>PROJECT: STUDIO.BOILERPLATE</span>
          <span className="text-gray-200">|</span>
          <span className="text-green-500 flex items-center gap-1">
            <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> SYNCED
          </span>
        </div>
        <div className="hidden sm:flex items-center space-x-6 text-[10px] text-gray-400 font-medium">
          <span>SCALE: 100%</span>
          <span>LATENCY: 12MS</span>
        </div>
      </footer>
    </div>
  );
}
