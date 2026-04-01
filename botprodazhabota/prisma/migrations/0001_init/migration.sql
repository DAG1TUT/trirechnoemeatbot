CREATE TABLE "Client" (
    "id" TEXT NOT NULL,
    "apiKey" TEXT NOT NULL,
    "businessName" TEXT NOT NULL,
    "businessType" TEXT,
    "systemPrompt" TEXT NOT NULL,
    "isActive" BOOLEAN NOT NULL DEFAULT true,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    CONSTRAINT "Client_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "Client_apiKey_key" ON "Client"("apiKey");
