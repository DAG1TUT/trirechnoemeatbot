ALTER TABLE "Client" ADD COLUMN "vkGroupId"     TEXT;
ALTER TABLE "Client" ADD COLUMN "vkAccessToken" TEXT;
ALTER TABLE "Client" ADD COLUMN "vkConfirmCode" TEXT;
ALTER TABLE "Client" ADD COLUMN "vkSecretKey"   TEXT;

CREATE UNIQUE INDEX "Client_vkGroupId_key" ON "Client"("vkGroupId");
