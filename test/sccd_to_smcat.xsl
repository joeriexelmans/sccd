<?xml version="1.0" encoding="UTF-8"?>
<!-- This XSLT transformation transforms SCCD source files to 'SMCAT', a textual format for state-machine-cat, a renderer of state machines -->
<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:sccd="msdl.uantwerpen.be/sccd">

  <xsl:output method="text"/>
  <xsl:template match="/">
    <xsl:for-each select="sccd:diagram/sccd:class">
      <xsl:apply-templates/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="sccd:scxml">
    <xsl:if test="@initial">
      initial_<xsl:value-of select="concat(string(count(ancestor::*)),'_',string(count(preceding-sibling::*)))"/>,
    </xsl:if>
    <xsl:apply-templates select="(sccd:state|sccd:parallel|sccd:history)[1]"/>
    <xsl:if test="@initial">
      initial_<xsl:value-of select="concat(string(count(ancestor::*)),'_',string(count(preceding-sibling::*)))"/>
      -> <xsl:value-of select="@initial"/>;
    </xsl:if>
  </xsl:template>

  <xsl:template match="sccd:state|sccd:parallel|sccd:history">
    <!-- [BEGIN-TEMPLATE-<xsl:value-of select="@id"/>] -->
    <xsl:value-of select="@id"/>

    <xsl:if test="self::sccd:parallel">
      [type=parallel]
    </xsl:if>
    <xsl:if test="(self::sccd:history)">
      <xsl:if test="@type = 'deep'">
        [type=deephistory]
      </xsl:if>
      <xsl:if test="not(@type = 'deep')">
        [type=history]
      </xsl:if>
    </xsl:if>

    <xsl:if test="sccd:state|sccd:parallel|sccd:history">
      {
        <xsl:if test="@initial">
          initial_<xsl:value-of select="concat(string(count(ancestor::*)),'_',string(count(preceding-sibling::*)))"/>,
        </xsl:if>
        <xsl:apply-templates select="(sccd:state|sccd:parallel|sccd:history)[1]"/>
      }
    </xsl:if>

    <xsl:choose>
      <xsl:when test="following-sibling::sccd:state | following-sibling::sccd:parallel | following-sibling::sccd:history">
        ,
        <!-- [NEXT-SIBLING] -->
        <xsl:apply-templates select="(following-sibling::sccd:state | following-sibling::sccd:parallel | following-sibling::sccd:history)[1]"/>
      </xsl:when>
      <xsl:otherwise>
        ;
      </xsl:otherwise>
    </xsl:choose>

    <xsl:if test="@initial">
      initial_<xsl:value-of select="concat(string(count(ancestor::*)),'_',string(count(preceding-sibling::*)))"/>
      -> <xsl:value-of select="@initial"/>;
    </xsl:if>

    <!-- [BEGIN-TRANSITIONS-<xsl:value-of select="@id"/>] -->
    <xsl:for-each select="sccd:transition">
      <xsl:value-of select="../@id"/> -> <xsl:value-of select="tokenize(@target,'/')[last()]"/>
      <xsl:if test="@event">
        : <xsl:value-of select="@event"/>
      </xsl:if>
      ;
    </xsl:for-each>
    <!-- [END-TRANSITIONS-<xsl:value-of select="@id"/>] -->

    <!-- [END-TEMPLATE-<xsl:value-of select="@id"/>] -->
  </xsl:template>

</xsl:stylesheet>

