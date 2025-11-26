"use client";

import Header from "@/components/Header";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import {
  MdArrowBack,
  MdCheckCircle,
  MdError,
  MdExpandLess,
  MdExpandMore,
  MdInfo,
  MdShield,
  MdTrendingDown,
  MdTrendingUp,
  MdWarning,
} from "react-icons/md";

interface ModelPrediction {
  model_name: string;
  prediction: string;
  confidence: number;
  type: string;
  contribution?: number;
  model_key?: string;
  features?: FeatureAnalysis[];
}

interface FeatureAnalysis {
  feature: string;
  value: number | string;
  impact: string;
  importance: number;
}

interface RiskFactor {
  factor: string;
  severity: string;
  description: string;
}

interface ExplanationData {
  model_breakdown: ModelPrediction[];
  feature_analysis: FeatureAnalysis[];
  risk_summary: {
    classification: string;
    risk_score: number;
    risk_level: string;
    risk_factors: RiskFactor[];
  };
  transaction: {
    id: number;
    user_id: number;
    username?: string;
    amount: number;
    merchant: string;
    classification: string;
    risk_score: number;
    status: string;
    created_at: string;
    payment_method?: string;
    ip_address?: string;
    device_id?: string;
  };
}

export default function TransactionDetailPage() {
  const params = useParams();
  const router = useRouter();
  const transactionId = params.id;

  const [data, setData] = useState<ExplanationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedModel, setExpandedModel] = useState<number | null>(null);

  useEffect(() => {
    fetchTransactionDetails();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [transactionId]);

  const fetchTransactionDetails = async () => {
    try {
      const token = localStorage.getItem("admin_token");
      const response = await fetch(
        `http://localhost:8000/api/v1/admin/transactions/${transactionId}/explain`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );

      if (response.ok) {
        const result = await response.json();
        console.log("Transaction details:", result); // Debug log
        console.log("Model breakdown:", result.model_breakdown); // Debug model data
        console.log("Model breakdown length:", result.model_breakdown?.length); // Debug length
        setData(result);
      } else {
        console.error(
          "Failed to fetch transaction details:",
          response.status,
          await response.text()
        );
      }
    } catch (error) {
      console.error("Failed to fetch transaction details:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-admin-bg min-h-screen">
        <Header title="Transaction Details" />
        <div className="p-8 text-center text-admin-text">Loading...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-admin-bg min-h-screen">
        <Header title="Transaction Details" />
        <div className="p-8 text-center text-admin-text-light">
          Transaction not found
        </div>
      </div>
    );
  }

  const getClassificationIcon = () => {
    switch (data.transaction.classification.toUpperCase()) {
      case "SAFE":
        return <MdCheckCircle className="text-green-500" />;
      case "SUSPICIOUS":
        return <MdWarning className="text-yellow-500" />;
      case "FRAUD":
        return <MdError className="text-red-500" />;
      default:
        return <MdInfo className="text-gray-500" />;
    }
  };

  const getClassificationColor = () => {
    switch (data.transaction.classification.toUpperCase()) {
      case "SAFE":
        return "border-green-500 bg-green-50";
      case "SUSPICIOUS":
        return "border-yellow-500 bg-yellow-50";
      case "FRAUD":
        return "border-red-500 bg-red-50";
      default:
        return "border-gray-500 bg-gray-50";
    }
  };

  return (
    <div className="bg-admin-bg min-h-screen">
      <Header title="Transaction Details" />

      <div className="p-8">
        {/* Back Button */}
        <button
          onClick={() => router.back()}
          className="flex items-center gap-2 text-primary-orange hover:text-yellow-600 mb-6 font-semibold transition-colors"
        >
          <MdArrowBack />
          Back to Transactions
        </button>

        {/* Transaction Overview */}
        <div
          className={`bg-white rounded-lg shadow-md p-6 mb-6 border-l-4 ${getClassificationColor()}`}
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="text-4xl">{getClassificationIcon()}</div>
            <div>
              <h2 className="text-2xl font-bold text-admin-text">
                Transaction #{data.transaction.id}
              </h2>
              <p className="text-admin-text-light">
                {new Date(data.transaction.created_at).toLocaleString()}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div>
              <p className="text-sm text-admin-text-light">User</p>
              <p className="text-xl font-semibold text-admin-text">
                {data.transaction.username ||
                  `User ${data.transaction.user_id}`}
              </p>
            </div>
            <div>
              <p className="text-sm text-admin-text-light">Amount</p>
              <p className="text-xl font-bold text-admin-text">
                ${data.transaction.amount.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm text-admin-text-light">Merchant</p>
              <p className="text-xl font-semibold text-admin-text">
                {data.transaction.merchant}
              </p>
            </div>
            <div>
              <p className="text-sm text-admin-text-light">Classification</p>
              <p className="text-xl font-bold text-admin-text">
                {data.transaction.classification}
              </p>
            </div>
            <div>
              <p className="text-sm text-admin-text-light">Risk Score</p>
              <p className="text-xl font-bold text-admin-text">
                {(data.transaction.risk_score * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          {data.transaction.ip_address && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-admin-text-light">IP Address: </span>
                  <span className="text-admin-text font-mono">
                    {data.transaction.ip_address}
                  </span>
                </div>
                <div>
                  <span className="text-admin-text-light">Device ID: </span>
                  <span className="text-admin-text font-mono">
                    {data.transaction.device_id}
                  </span>
                </div>
                <div>
                  <span className="text-admin-text-light">
                    Payment Method:{" "}
                  </span>
                  <span className="text-admin-text">
                    {data.transaction.payment_method}
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* AI Models Breakdown */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-4">
              <MdShield className="text-2xl text-primary-orange" />
              <h3 className="text-xl font-bold text-admin-text">
                AI Models Analysis
              </h3>
            </div>
            <p className="text-sm text-admin-text-light mb-4">
              11 AI models analyzed this transaction
            </p>

            {/* Model Performance Chart */}
            {data.model_breakdown && data.model_breakdown.length > 0 && (
              <div className="mb-6 bg-gradient-to-br from-orange-50 to-yellow-50 rounded-lg p-4 border border-orange-200">
                <h4 className="font-semibold text-admin-text mb-3 text-sm">
                  Model Confidence Overview
                </h4>
                <div className="space-y-2">
                  {data.model_breakdown.map((model, index) => {
                    const getModelColor = (
                      type: string,
                      confidence: number
                    ) => {
                      if (type.includes("Machine Learning")) {
                        return confidence > 0.7
                          ? "bg-blue-500"
                          : confidence > 0.4
                          ? "bg-blue-400"
                          : "bg-blue-300";
                      } else if (type.includes("Deep Learning")) {
                        return confidence > 0.7
                          ? "bg-purple-500"
                          : confidence > 0.4
                          ? "bg-purple-400"
                          : "bg-purple-300";
                      } else {
                        return confidence > 0.7
                          ? "bg-orange-500"
                          : confidence > 0.4
                          ? "bg-orange-400"
                          : "bg-orange-300";
                      }
                    };

                    // Ensure minimum visible width for very low confidence scores
                    const barWidth = Math.max(
                      model.confidence * 100,
                      model.confidence > 0 ? 2 : 0
                    );

                    return (
                      <div key={index} className="flex items-center gap-2">
                        <span
                          className="text-xs text-admin-text-light w-32 truncate"
                          title={model.model_name}
                        >
                          {model.model_name}
                        </span>
                        <div className="flex-1 bg-gray-200 rounded-full h-4 relative overflow-hidden">
                          <div
                            className={`h-4 rounded-full transition-all duration-500 ${getModelColor(
                              model.type,
                              model.confidence
                            )}`}
                            style={{ width: `${barWidth}%` }}
                          >
                            <div className="absolute inset-0 bg-gradient-to-r from-transparent to-white opacity-30"></div>
                          </div>
                        </div>
                        <span className="text-xs font-semibold text-admin-text w-12 text-right">
                          {model.confidence < 0.01
                            ? "<1"
                            : (model.confidence * 100).toFixed(0)}
                          %
                        </span>
                      </div>
                    );
                  })}
                </div>
                <div className="mt-3 pt-3 border-t border-orange-200 flex gap-4 text-xs">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-blue-500 rounded"></div>
                    <span className="text-admin-text-light">ML Models</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-purple-500 rounded"></div>
                    <span className="text-admin-text-light">DL Models</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 bg-orange-500 rounded"></div>
                    <span className="text-admin-text-light">Ensemble</span>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-3">
              {data.model_breakdown && data.model_breakdown.length > 0 ? (
                data.model_breakdown.map((model, index) => {
                  const isExpanded = expandedModel === index;
                  const getModelGradient = (type: string) => {
                    if (type.includes("Machine Learning")) {
                      return "from-blue-50 to-blue-100";
                    } else if (type.includes("Deep Learning")) {
                      return "from-purple-50 to-purple-100";
                    } else {
                      return "from-orange-50 to-orange-100";
                    }
                  };

                  const getBorderColor = (type: string) => {
                    if (type.includes("Machine Learning")) {
                      return "border-blue-200 hover:border-blue-300";
                    } else if (type.includes("Deep Learning")) {
                      return "border-purple-200 hover:border-purple-300";
                    } else {
                      return "border-orange-200 hover:border-orange-300";
                    }
                  };

                  const getIconColor = (type: string) => {
                    if (type.includes("Machine Learning")) {
                      return "text-blue-600";
                    } else if (type.includes("Deep Learning")) {
                      return "text-purple-600";
                    } else {
                      return "text-orange-600";
                    }
                  };

                  return (
                    <div
                      key={index}
                      className={`border-2 rounded-xl overflow-hidden transition-all duration-300 ${getBorderColor(
                        model.type
                      )} ${
                        isExpanded ? "shadow-lg" : "shadow-sm hover:shadow-md"
                      }`}
                    >
                      {/* Card Header - Always Visible */}
                      <div
                        className={`bg-gradient-to-r ${getModelGradient(
                          model.type
                        )} p-4 cursor-pointer`}
                        onClick={() =>
                          setExpandedModel(isExpanded ? null : index)
                        }
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex items-start gap-3">
                            <div
                              className={`p-2 bg-white rounded-lg shadow-sm ${getIconColor(
                                model.type
                              )}`}
                            >
                              <MdShield className="w-5 h-5" />
                            </div>
                            <div>
                              <p className="font-semibold text-admin-text text-lg">
                                {model.model_name}
                              </p>
                              <p className="text-xs text-admin-text-light mt-0.5">
                                {model.type}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            <span
                              className={`px-3 py-1.5 text-xs font-bold rounded-full shadow-sm ${
                                model.prediction === "FRAUD"
                                  ? "bg-red-500 text-white"
                                  : model.prediction === "SUSPICIOUS"
                                  ? "bg-yellow-500 text-white"
                                  : "bg-green-500 text-white"
                              }`}
                            >
                              {model.prediction}
                            </span>
                            {isExpanded ? (
                              <MdExpandLess className="w-6 h-6 text-admin-text-light" />
                            ) : (
                              <MdExpandMore className="w-6 h-6 text-admin-text-light" />
                            )}
                          </div>
                        </div>

                        {/* Confidence Bar */}
                        <div className="mt-4">
                          <div className="flex justify-between text-sm mb-2">
                            <span className="text-admin-text-light font-medium">
                              Confidence Level
                            </span>
                            <span className="text-admin-text font-bold">
                              {model.confidence < 0.01
                                ? "<1"
                                : (model.confidence * 100).toFixed(1)}
                              %
                            </span>
                          </div>
                          <div className="w-full bg-white rounded-full h-3 shadow-inner">
                            <div
                              className={`h-3 rounded-full transition-all duration-500 ${
                                model.confidence > 0.7
                                  ? "bg-gradient-to-r from-green-400 to-green-600"
                                  : model.confidence > 0.4
                                  ? "bg-gradient-to-r from-yellow-400 to-yellow-600"
                                  : "bg-gradient-to-r from-red-400 to-red-600"
                              }`}
                              style={{
                                width: `${Math.max(
                                  model.confidence * 100,
                                  2
                                )}%`,
                              }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Expanded Details Section */}
                      {isExpanded && (
                        <div className="bg-white p-5 border-t-2 border-gray-100">
                          <div className="mb-4">
                            <h4 className="text-sm font-bold text-admin-text mb-3 flex items-center gap-2">
                              <MdInfo
                                className={`w-4 h-4 ${getIconColor(
                                  model.type
                                )}`}
                              />
                              Why {model.model_name} predicted{" "}
                              {model.prediction}
                            </h4>
                            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                              <p className="text-sm text-admin-text-light leading-relaxed">
                                {model.prediction === "FRAUD" ? (
                                  <>
                                    This model detected patterns strongly
                                    associated with fraudulent activity. The
                                    confidence level of{" "}
                                    <span className="font-bold text-red-600">
                                      {(model.confidence * 100).toFixed(1)}%
                                    </span>{" "}
                                    indicates high certainty that this
                                    transaction exhibits anomalous behavior
                                    based on historical fraud patterns.
                                  </>
                                ) : model.prediction === "SUSPICIOUS" ? (
                                  <>
                                    This model found moderate risk indicators
                                    that warrant attention. The confidence level
                                    of{" "}
                                    <span className="font-bold text-yellow-600">
                                      {(model.confidence * 100).toFixed(1)}%
                                    </span>{" "}
                                    suggests some unusual patterns were
                                    detected, but they&apos;re not definitively
                                    fraudulent.
                                  </>
                                ) : (
                                  <>
                                    This model determined the transaction
                                    follows normal patterns. The low confidence
                                    score of{" "}
                                    <span className="font-bold text-green-600">
                                      {model.confidence < 0.01
                                        ? "<1"
                                        : (model.confidence * 100).toFixed(1)}
                                      %
                                    </span>{" "}
                                    indicates minimal fraud probability based on
                                    learned legitimate transaction behaviors.
                                  </>
                                )}
                              </p>
                            </div>
                          </div>

                          {/* Key Contributing Factors - Model Specific */}
                          {model.features && model.features.length > 0 && (
                            <div>
                              <h4 className="text-sm font-bold text-admin-text mb-3 flex items-center gap-2">
                                <MdTrendingUp
                                  className={`w-4 h-4 ${getIconColor(
                                    model.type
                                  )}`}
                                />
                                Top Contributing Factors for {model.model_name}
                              </h4>
                              <div className="space-y-2">
                                {model.features.map((feature, idx) => (
                                  <div
                                    key={idx}
                                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
                                  >
                                    <div className="flex items-center gap-3 flex-1">
                                      <div
                                        className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white ${
                                          feature.impact === "POSITIVE"
                                            ? "bg-gradient-to-br from-red-400 to-red-600"
                                            : feature.impact === "NEGATIVE"
                                            ? "bg-gradient-to-br from-green-400 to-green-600"
                                            : "bg-gradient-to-br from-gray-400 to-gray-600"
                                        }`}
                                      >
                                        {idx + 1}
                                      </div>
                                      <div className="flex-1">
                                        <p className="text-sm font-semibold text-admin-text">
                                          {feature.feature
                                            .replace(/_/g, " ")
                                            .replace(/\b\w/g, (l) =>
                                              l.toUpperCase()
                                            )}
                                        </p>
                                        <p className="text-xs text-admin-text-light">
                                          Value:{" "}
                                          <span className="font-medium">
                                            {typeof feature.value === "number"
                                              ? feature.value.toFixed(2)
                                              : feature.value}
                                          </span>
                                        </p>
                                      </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      {feature.impact === "POSITIVE" ? (
                                        <MdTrendingUp className="w-5 h-5 text-red-500" />
                                      ) : feature.impact === "NEGATIVE" ? (
                                        <MdTrendingDown className="w-5 h-5 text-green-500" />
                                      ) : (
                                        <div className="w-5 h-5" />
                                      )}
                                      <div className="text-right">
                                        <p
                                          className={`text-xs font-bold ${
                                            feature.impact === "POSITIVE"
                                              ? "text-red-600"
                                              : feature.impact === "NEGATIVE"
                                              ? "text-green-600"
                                              : "text-gray-600"
                                          }`}
                                        >
                                          {feature.impact === "POSITIVE"
                                            ? "Increases"
                                            : feature.impact === "NEGATIVE"
                                            ? "Decreases"
                                            : "Neutral"}
                                        </p>
                                        <p className="text-xs text-admin-text-light">
                                          Risk
                                        </p>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Model Type Info */}
                          <div
                            className={`mt-4 p-3 rounded-lg bg-gradient-to-r ${getModelGradient(
                              model.type
                            )} border ${getBorderColor(model.type)}`}
                          >
                            <p className="text-xs text-admin-text-light">
                              <span className="font-semibold">Model Type:</span>{" "}
                              {model.type}
                              {model.type.includes("Machine Learning") && (
                                <span className="ml-2">
                                  • Uses traditional statistical patterns and
                                  feature engineering
                                </span>
                              )}
                              {model.type.includes("Deep Learning") && (
                                <span className="ml-2">
                                  • Uses neural networks to detect complex
                                  patterns
                                </span>
                              )}
                              {model.type.includes("Ensemble") && (
                                <span className="ml-2">
                                  • Combines predictions from all models for
                                  final decision
                                </span>
                              )}
                            </p>
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })
              ) : (
                <p className="text-admin-text-light text-sm">
                  No model predictions available
                </p>
              )}
            </div>
          </div>

          {/* Risk Factors */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center gap-2 mb-4">
              <MdWarning className="text-2xl text-yellow-500" />
              <h3 className="text-xl font-bold text-admin-text">
                Risk Analysis
              </h3>
            </div>

            <div className="mb-6">
              <p className="text-sm text-admin-text-light mb-2">
                Overall Risk Level
              </p>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full ${
                      data.risk_summary.risk_score > 0.7
                        ? "bg-red-500"
                        : data.risk_summary.risk_score > 0.4
                        ? "bg-yellow-500"
                        : "bg-green-500"
                    }`}
                    style={{ width: `${data.risk_summary.risk_score * 100}%` }}
                  />
                </div>
                <span className="text-2xl font-bold text-admin-text">
                  {(data.risk_summary.risk_score * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-sm font-semibold text-admin-text mt-2">
                {data.risk_summary.risk_level}
              </p>
            </div>

            <div className="space-y-3">
              <h4 className="font-semibold text-admin-text mb-2">
                Risk Factors Detected:
              </h4>
              {data.risk_summary.risk_factors &&
              data.risk_summary.risk_factors.length > 0 ? (
                data.risk_summary.risk_factors.map((factor, index) => (
                  <div
                    key={index}
                    className="border-l-4 border-yellow-400 bg-yellow-50 p-3 rounded"
                  >
                    <div className="flex items-start gap-2">
                      <MdWarning className="text-yellow-600 mt-0.5 flex-shrink-0" />
                      <div>
                        <p className="font-semibold text-admin-text text-sm">
                          {factor.factor}
                        </p>
                        <p className="text-xs text-admin-text-light mt-1">
                          {factor.description}
                        </p>
                        <span
                          className={`inline-block mt-1 px-2 py-0.5 text-xs font-semibold rounded ${
                            factor.severity === "HIGH"
                              ? "bg-red-100 text-red-800"
                              : factor.severity === "MEDIUM"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-blue-100 text-blue-800"
                          }`}
                        >
                          {factor.severity} SEVERITY
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="border-l-4 border-green-400 bg-green-50 p-3 rounded">
                  <div className="flex items-start gap-2">
                    <MdCheckCircle className="text-green-600 mt-0.5 flex-shrink-0" />
                    <div>
                      <p className="font-semibold text-admin-text text-sm">
                        No significant risk factors detected
                      </p>
                      <p className="text-xs text-admin-text-light mt-1">
                        Transaction appears normal
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Feature Analysis */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-admin-text mb-4">
            Feature Analysis
          </h3>
          <p className="text-sm text-admin-text-light mb-4">
            Key features that influenced the AI decision
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {data.feature_analysis && data.feature_analysis.length > 0 ? (
              data.feature_analysis.map((feature, index) => (
                <div
                  key={index}
                  className="border border-gray-200 rounded-lg p-4"
                >
                  <div className="flex justify-between items-start mb-2">
                    <p className="font-semibold text-admin-text">
                      {feature.feature}
                    </p>
                    <span
                      className={`px-2 py-1 text-xs font-semibold rounded ${
                        feature.impact === "POSITIVE"
                          ? "bg-green-100 text-green-800"
                          : feature.impact === "NEGATIVE"
                          ? "bg-red-100 text-red-800"
                          : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {feature.impact}
                    </span>
                  </div>
                  <p className="text-sm text-admin-text-light mb-2">
                    Value:{" "}
                    <span className="text-admin-text font-medium">
                      {feature.value}
                    </span>
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                      <div
                        className="bg-admin-primary h-1.5 rounded-full"
                        style={{ width: `${feature.importance * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-admin-text-light">
                      {(feature.importance * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-admin-text-light text-sm col-span-2">
                No feature analysis available
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
