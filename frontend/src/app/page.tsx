'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { FiSearch, FiLoader, FiCheckCircle, FiAlertCircle } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

interface CompanyInfo {
  basic_info: {
    company_name: string;
    business_description: string;
    address: string;
    representative: string;
    tel: string;
    business_hours: string;
  };
  analysis: {
    summary: string;
    investor_analysis: string;
    job_seeker_info: string;
  };
}

export default function Home() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo | null>(null);
  const [activeTab, setActiveTab] = useState('basic');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) {
      toast.error('URLを入力してください');
      return;
    }

    setIsLoading(true);
    setCompanyInfo(null);

    try {
      const response = await fetch('http://localhost:8000/api/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setCompanyInfo(data);
      toast.success('企業情報を取得しました');
    } catch (error) {
      toast.error('エラーが発生しました: ' + (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-white p-8">
      <div className="max-w-4xl mx-auto">
        <motion.h1 
          className="text-4xl font-bold text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          企業情報アナライザー
        </motion.h1>

        <motion.form 
          onSubmit={handleSubmit}
          className="mb-8"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <div className="flex gap-4">
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="企業のWebサイトURLを入力"
              className="flex-1 px-4 py-3 rounded-lg bg-gray-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50"
            >
              {isLoading ? <FiLoader className="animate-spin" /> : <FiSearch />}
              分析開始
            </button>
          </div>
        </motion.form>

        {companyInfo && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-gray-800 rounded-xl p-6 shadow-xl"
          >
            <div className="flex gap-4 mb-6">
              <button
                onClick={() => setActiveTab('basic')}
                className={`flex-1 py-2 rounded-lg transition-colors ${
                  activeTab === 'basic' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                基本情報
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`flex-1 py-2 rounded-lg transition-colors ${
                  activeTab === 'analysis' ? 'bg-blue-600' : 'bg-gray-700 hover:bg-gray-600'
                }`}
              >
                AI分析
              </button>
            </div>

            {activeTab === 'basic' ? (
              <div className="space-y-4">
                <InfoItem label="会社名" value={companyInfo.basic_info.company_name} />
                <InfoItem label="事業内容" value={companyInfo.basic_info.business_description} />
                <InfoItem label="所在地" value={companyInfo.basic_info.address} />
                <InfoItem label="代表者" value={companyInfo.basic_info.representative} />
                <InfoItem label="電話番号" value={companyInfo.basic_info.tel} />
                <InfoItem label="営業時間" value={companyInfo.basic_info.business_hours} />
              </div>
            ) : (
              <div className="space-y-6">
                <AnalysisItem 
                  title="企業概要" 
                  content={companyInfo.analysis.summary}
                  icon={<FiCheckCircle className="text-green-400" />}
                />
                <AnalysisItem 
                  title="投資家向け分析" 
                  content={companyInfo.analysis.investor_analysis}
                  icon={<FiCheckCircle className="text-blue-400" />}
                />
                <AnalysisItem 
                  title="就職活動者向け情報" 
                  content={companyInfo.analysis.job_seeker_info}
                  icon={<FiCheckCircle className="text-purple-400" />}
                />
              </div>
            )}
          </motion.div>
        )}
      </div>
    </main>
  );
}

const InfoItem = ({ label, value }: { label: string; value: string }) => (
  <div className="bg-gray-700 rounded-lg p-4">
    <div className="text-gray-400 text-sm mb-1">{label}</div>
    <div className="text-white">{value || '情報なし'}</div>
  </div>
);

const AnalysisItem = ({ title, content, icon }: { title: string; content: string; icon: React.ReactNode }) => (
  <div className="bg-gray-700 rounded-lg p-4">
    <div className="flex items-center gap-2 mb-2">
      {icon}
      <h3 className="text-lg font-semibold">{title}</h3>
    </div>
    <p className="text-gray-300">{content}</p>
  </div>
);